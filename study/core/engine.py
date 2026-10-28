from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

from study.core.models import (
    AppliedAnswer,
    MasteryPolicy,
    ReviewItem,
    TopicStats,
    learning_state,
)


def apply_answer(
    stats: TopicStats,
    review: ReviewItem | None,
    *,
    correct: bool,
    question_id: str,
    now: datetime,
    policy: MasteryPolicy,
    counts_as_evidence: bool = True,
) -> AppliedAnswer:
    """Atualiza domínio e fila sem apagar o histórico.

    Um acerto isolado não tira a questão da fila. Um erro zera a sequência.
    A linha da fila permanece quando deixa de estar ativa.
    """
    if stats.course_id == "":
        raise ValueError("A resposta precisa de um curso.")
    updated = replace(stats)
    stamp = now.isoformat(timespec="seconds")

    if counts_as_evidence:
        updated.attempts += 1
        if correct:
            updated.correct += 1
            updated.consecutive_correct += 1
        else:
            updated.incorrect += 1
            updated.consecutive_correct = 0
        updated.last_studied_at = stamp

    queued = None if review is None else replace(review)
    cleared = False

    if not correct:
        if queued is None:
            queued = ReviewItem(
                course_id=stats.course_id,
                question_id=question_id,
                topic_id=stats.topic_id,
                consecutive_correct=0,
                reason="error",
                active=True,
                entered_at=stamp,
                last_attempt_at=stamp,
            )
        else:
            queued.consecutive_correct = 0
            queued.reason = "error"
            queued.active = True
            queued.last_attempt_at = stamp
            if not queued.entered_at:
                queued.entered_at = stamp
        updated.next_review_at = stamp
    else:
        if queued is not None and queued.active and queued.reason == "error":
            queued.consecutive_correct += 1
            queued.last_attempt_at = stamp
            if queued.consecutive_correct >= policy.consecutive_to_clear:
                queued.active = False
                cleared = True
        if counts_as_evidence:
            pending_after = 1 if queued is not None and queued.active and queued.reason == "error" else 0
            state = learning_state(updated, pending_after, policy)
            days = 7 if state == "dominado" else 1
            updated.next_review_at = (now + timedelta(days=days)).isoformat(timespec="seconds")

    return AppliedAnswer(stats=updated, review=queued, cleared_review=cleared)

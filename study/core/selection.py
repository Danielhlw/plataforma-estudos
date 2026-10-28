from __future__ import annotations

import random
from collections.abc import Sequence
from datetime import datetime

from study.core.models import MasteryPolicy, QuestionRef, ReviewItem, TopicStats, is_mastered


_FRACTIONS = (
    ("unseen", 0.25),
    ("recent_errors", 0.25),
    ("below_threshold", 0.20),
    ("due_review", 0.15),
    ("exam_important", 0.10),
    ("maintenance", 0.05),
)


def _quotas(count: int) -> dict[str, int]:
    raw = {name: count * fraction for name, fraction in _FRACTIONS}
    assigned = {name: int(value) for name, value in raw.items()}
    leftover = count - sum(assigned.values())
    remainders = sorted(raw, key=lambda name: raw[name] - assigned[name], reverse=True)
    for name in remainders[:leftover]:
        assigned[name] += 1
    return assigned


def _due(stats: TopicStats | None, now: datetime) -> bool:
    if stats is None or not stats.next_review_at:
        return False
    return stats.next_review_at <= now.isoformat(timespec="seconds")


def select_daily(
    questions: Sequence[QuestionRef],
    stats_by_topic: dict[str, TopicStats],
    queue: Sequence[ReviewItem],
    recent_question_ids: Sequence[str],
    *,
    count: int,
    now: datetime,
    policy: MasteryPolicy,
    answer_counts: dict[str, int] | None = None,
) -> list[QuestionRef]:
    """Escolhe questões da sessão diária sem repetir o mesmo id na sessão.

    Se o tópico tiver outra questão ainda não usada recentemente, essa
    alternativa vem antes da questão recém-respondida.
    """
    if count < 1:
        return []
    answer_counts = answer_counts or {}
    recent = set(recent_question_ids)
    eligible = [q for q in questions if q.exercise_type == "mcq"]
    by_id = {q.question_id: q for q in eligible}
    active_errors = [
        item for item in queue if item.active and item.reason == "error" and item.question_id in by_id
    ]
    error_ids = {item.question_id for item in active_errors}

    def pending_for(topic_id: str) -> int:
        return sum(1 for item in active_errors if item.topic_id == topic_id)

    def pool_unseen() -> list[QuestionRef]:
        return [q for q in eligible if stats_by_topic.get(q.topic_id, TopicStats("", q.topic_id)).attempts == 0]

    def pool_errors() -> list[QuestionRef]:
        ordered = sorted(active_errors, key=lambda item: item.last_attempt_at or item.entered_at, reverse=True)
        return [by_id[item.question_id] for item in ordered]

    def pool_below() -> list[QuestionRef]:
        found = []
        for question in eligible:
            stats = stats_by_topic.get(question.topic_id)
            if stats is None or stats.attempts == 0:
                continue
            accuracy = stats.accuracy or 0.0
            if accuracy < policy.threshold or stats.attempts < policy.min_evidence:
                found.append(question)
        return found

    def pool_due() -> list[QuestionRef]:
        found = []
        for question in eligible:
            if question.question_id in error_ids or _due(stats_by_topic.get(question.topic_id), now):
                found.append(question)
        return found

    def pool_important() -> list[QuestionRef]:
        return [q for q in eligible if q.exam_importance > 0 and not is_mastered(
            stats_by_topic.get(q.topic_id, TopicStats("", q.topic_id)),
            pending_for(q.topic_id),
            policy,
        )]

    def pool_maintenance() -> list[QuestionRef]:
        return [q for q in eligible if is_mastered(
            stats_by_topic.get(q.topic_id, TopicStats("", q.topic_id)),
            pending_for(q.topic_id),
            policy,
        )]

    pools = {
        "unseen": pool_unseen(),
        "recent_errors": pool_errors(),
        "below_threshold": pool_below(),
        "due_review": pool_due(),
        "exam_important": pool_important(),
        "maintenance": pool_maintenance(),
    }

    def sort_key(question: QuestionRef) -> tuple:
        same_topic_fresh = any(
            other.topic_id == question.topic_id
            and other.question_id != question.question_id
            and other.question_id not in recent
            for other in eligible
        )
        prefer_skip = 1 if question.question_id in recent and same_topic_fresh else 0
        return (
            prefer_skip,
            1 if question.question_id in recent else 0,
            answer_counts.get(question.question_id, 0),
            -question.exam_importance,
            question.difficulty,
            question.question_id,
        )

    for name in pools:
        pools[name] = sorted(pools[name], key=sort_key)

    selected: list[QuestionRef] = []
    used: set[str] = set()

    def take(candidates: list[QuestionRef], limit: int) -> None:
        got = 0
        for question in candidates:
            if got >= limit or len(selected) >= count:
                return
            if question.question_id in used:
                continue
            selected.append(question)
            used.add(question.question_id)
            got += 1

    for name, slots in _quotas(count).items():
        take(pools[name], slots)

    priority = ["unseen", "recent_errors", "below_threshold", "due_review", "exam_important", "maintenance"]
    guard = 0
    while len(selected) < count and guard < count * 6:
        guard += 1
        before = len(selected)
        for name in priority:
            if len(selected) >= count:
                break
            take(pools[name], 1)
        if len(selected) == before:
            break

    if len(selected) < count:
        take(sorted(eligible, key=sort_key), count - len(selected))
    return selected[:count]


def select_exam(
    questions: Sequence[QuestionRef],
    distribution: dict[str, int],
    rng: random.Random | None = None,
) -> list[QuestionRef]:
    """Monta o simulado só quando cada bloco tem questões suficientes."""
    rng = rng or random.Random()
    chosen: list[QuestionRef] = []
    for module_id, needed in distribution.items():
        pool = [q for q in questions if q.module_id == module_id and q.exercise_type == "mcq"]
        if len(pool) < needed:
            raise ValueError(
                f"O bloco {module_id} tem {len(pool)} questões de treino e o simulado pede {needed}."
            )
        picked = pool[:]
        rng.shuffle(picked)
        chosen.extend(picked[:needed])
    rng.shuffle(chosen)
    return chosen

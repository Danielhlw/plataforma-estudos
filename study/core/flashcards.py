from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CardProgress:
    course_id: str
    card_id: str
    repetitions: int = 0
    interval_days: float = 0
    ease: float = 2.5
    due_at: str | None = None
    last_grade: str | None = None


def grade_card(card: CardProgress, grade: str, now: datetime) -> CardProgress:
    """Repetição espaçada simples. grade: again, hard, good, easy."""
    updated = CardProgress(
        course_id=card.course_id,
        card_id=card.card_id,
        repetitions=card.repetitions,
        interval_days=card.interval_days,
        ease=card.ease,
        due_at=card.due_at,
        last_grade=grade,
    )
    if grade == "again":
        updated.repetitions = 0
        updated.interval_days = 0
        updated.due_at = now.isoformat(timespec="seconds")
        updated.ease = max(1.3, updated.ease - 0.2)
        return updated
    updated.repetitions += 1
    if updated.repetitions == 1:
        updated.interval_days = 1
    elif updated.repetitions == 2:
        updated.interval_days = 3
    else:
        updated.interval_days = max(1, round(updated.interval_days * updated.ease))
    if grade == "easy":
        updated.ease = min(3.0, updated.ease + 0.1)
        updated.interval_days = max(updated.interval_days, 4)
    elif grade == "hard":
        updated.ease = max(1.3, updated.ease - 0.15)
        updated.interval_days = max(1, round(updated.interval_days * 0.7))
    updated.due_at = (now + timedelta(days=updated.interval_days)).isoformat(timespec="seconds")
    return updated

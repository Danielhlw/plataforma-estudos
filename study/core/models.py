from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class MasteryPolicy:
    threshold: float = 0.8
    min_evidence: int = 5
    consecutive_to_clear: int = 2

    def __post_init__(self) -> None:
        if not 0 < self.threshold <= 1:
            raise ValueError("O limiar de domínio deve estar entre 0 e 1.")
        if self.min_evidence < 1:
            raise ValueError("O mínimo de evidências deve ser pelo menos 1.")
        if self.consecutive_to_clear < 2:
            raise ValueError("A fila de erros exige pelo menos dois acertos consecutivos.")


@dataclass
class TopicStats:
    course_id: str
    topic_id: str
    attempts: int = 0
    correct: int = 0
    incorrect: int = 0
    consecutive_correct: int = 0
    last_studied_at: str | None = None
    next_review_at: str | None = None

    @property
    def accuracy(self) -> float | None:
        if self.attempts == 0:
            return None
        return self.correct / self.attempts


@dataclass
class ReviewItem:
    course_id: str
    question_id: str
    topic_id: str
    consecutive_correct: int = 0
    reason: str = "error"
    active: bool = True
    entered_at: str = ""
    last_attempt_at: str | None = None


@dataclass(frozen=True)
class QuestionRef:
    question_id: str
    topic_id: str
    module_id: str
    difficulty: int = 1
    exam_importance: int = 0
    exercise_type: str = "mcq"


@dataclass
class AppliedAnswer:
    stats: TopicStats
    review: ReviewItem | None
    cleared_review: bool


def learning_state(stats: TopicStats, pending_errors: int, policy: MasteryPolicy) -> str:
    """Estado do tópico a partir das evidências gravadas.

    A percentagem só declara domínio com o mínimo de tentativas e sem
    questões deste tópico ainda ativas na fila de erros.
    """
    if stats.attempts == 0 and pending_errors == 0:
        return "nao_estudado"
    if pending_errors > 0:
        return "em_revisao"
    accuracy = stats.accuracy or 0.0
    if stats.attempts >= policy.min_evidence and accuracy >= policy.threshold:
        return "dominado"
    return "em_aprendizagem"


def confidence(stats: TopicStats, pending_errors: int, policy: MasteryPolicy) -> float:
    if stats.attempts == 0:
        return 0.0
    evidence = min(1.0, stats.attempts / policy.min_evidence)
    accuracy = stats.correct / stats.attempts
    score = accuracy * evidence
    if pending_errors:
        score *= 0.5
    return round(min(1.0, max(0.0, score)), 4)


def is_mastered(stats: TopicStats, pending_errors: int, policy: MasteryPolicy) -> bool:
    return learning_state(stats, pending_errors, policy) == "dominado"


@dataclass
class AnswerEvent:
    course_id: str
    question_id: str
    topic_id: str
    module_id: str
    chosen_answer: str
    correct_answer: str
    is_correct: bool
    mode: str
    answered_at: datetime
    question_text: str = ""
    counts_as_evidence: bool = True
    session_id: int | None = None
    extra: dict = field(default_factory=dict)

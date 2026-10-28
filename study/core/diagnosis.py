from __future__ import annotations

from dataclasses import dataclass, field

from study.core.models import MasteryPolicy, ReviewItem, TopicStats, learning_state


@dataclass
class Recommendation:
    action: str
    summary: str
    course_id: str
    module_id: str | None = None
    topic_id: str | None = None
    session_id: int | None = None


@dataclass
class Diagnosis:
    course_id: str
    total: int
    correct: int
    accuracy: float | None
    by_module: dict[str, dict[str, float | int | None]]
    by_topic: dict[str, dict[str, float | int | None]]
    errors: list[dict]
    still_in_queue: list[str]
    comparison: str
    recommendation: Recommendation
    warnings: list[str] = field(default_factory=list)

    @property
    def score_label(self) -> str:
        if self.total == 0:
            return "Sem respostas nesta sessão."
        return f"{self.correct} de {self.total}"


def _bucket(rows: list[dict], key: str) -> dict[str, dict[str, float | int | None]]:
    grouped: dict[str, dict[str, float | int | None]] = {}
    for row in rows:
        name = row[key]
        slot = grouped.setdefault(name, {"total": 0, "correct": 0, "accuracy": None})
        slot["total"] = int(slot["total"] or 0) + 1
        slot["correct"] = int(slot["correct"] or 0) + (1 if row["is_correct"] else 0)
    for slot in grouped.values():
        total = int(slot["total"] or 0)
        slot["accuracy"] = (int(slot["correct"] or 0) / total) if total else None
    return grouped


def compare_with_previous(current: float | None, previous: float | None) -> str:
    if current is None:
        return "Esta sessão não tem respostas para comparar."
    if previous is None:
        return "Ainda não há uma sessão anterior concluída deste tipo para comparar."
    delta = round((current - previous) * 100)
    if delta > 0:
        return (
            f"Aproveitamento de {current:.0%} nesta sessão, "
            f"{delta} pontos percentuais acima da sessão anterior ({previous:.0%})."
        )
    if delta < 0:
        return (
            f"Aproveitamento de {current:.0%} nesta sessão, "
            f"{abs(delta)} pontos percentuais abaixo da sessão anterior ({previous:.0%})."
        )
    return f"Aproveitamento de {current:.0%}, igual ao da sessão anterior."


def recommend(
    *,
    course_id: str,
    course_title: str,
    modules: list[dict],
    stats_by_topic: dict[str, TopicStats],
    queue: list[ReviewItem],
    lesson_status: dict[str, str],
    active_session: dict | None,
    question_count: int,
    exam_ready: bool,
    policy: MasteryPolicy,
) -> Recommendation:
    """Próximo passo a partir do estado gravado, sem texto genérico."""
    if active_session is not None:
        kind = active_session.get("kind", "estudo")
        return Recommendation(
            action="continue",
            summary=f"Há uma sessão de {kind} inacabada em {course_title}.",
            course_id=course_id,
            session_id=active_session.get("id"),
        )

    pending = [item for item in queue if item.active and item.reason == "error"]
    if pending:
        topic_id = pending[0].topic_id
        return Recommendation(
            action="review",
            summary=f"{len(pending)} questão(ões) de {course_title} continuam na fila de erros.",
            course_id=course_id,
            topic_id=topic_id,
        )

    if question_count == 0:
        return Recommendation(
            action="notebook" if course_id == "english" else "lesson",
            summary=(
                f"{course_title} ainda não tem questões praticáveis. "
                "O caderno de inglês está vazio."
                if course_id == "english"
                else f"{course_title} ainda não tem questões carregadas."
            ),
            course_id=course_id,
        )

    for module in modules:
        status = lesson_status.get(module["id"], "not_started")
        if status not in {"completed", "skipped"} and module.get("question_count", 0) > 0:
            return Recommendation(
                action="lesson",
                summary=f"A lição «{module['title']}» ainda não foi concluída nem dispensada.",
                course_id=course_id,
                module_id=module["id"],
            )

    weakest: tuple[float, int, str, str] | None = None
    for module in modules:
        for topic in module["topics"]:
            if topic.get("question_count", 0) == 0:
                continue
            stats = stats_by_topic.get(topic["id"], TopicStats(course_id, topic["id"]))
            pending_topic = sum(1 for item in pending if item.topic_id == topic["id"])
            state = learning_state(stats, pending_topic, policy)
            if state == "dominado":
                continue
            accuracy = stats.accuracy if stats.accuracy is not None else -1.0
            candidate = (accuracy, -stats.attempts, topic["id"], topic["name"])
            if weakest is None or candidate < weakest:
                weakest = candidate
    if weakest is not None and weakest[0] >= 0:
        return Recommendation(
            action="practice",
            summary=(
                f"«{weakest[3]}» está em {weakest[0]:.0%} "
                f"com {abs(weakest[1])} tentativa(s). O objetivo é {policy.threshold:.0%} "
                f"e pelo menos {policy.min_evidence} evidências."
            ),
            course_id=course_id,
            topic_id=weakest[2],
        )
    if weakest is not None:
        return Recommendation(
            action="practice",
            summary=f"«{weakest[3]}» ainda não tem tentativas registadas.",
            course_id=course_id,
            topic_id=weakest[2],
        )

    if exam_ready and course_id == "cnh-al":
        return Recommendation(
            action="exam",
            summary=(
                "Os tópicos com questões já atingiram o critério de domínio gravado. "
                "Um simulado de 30 questões mede o conjunto, sem feedback no meio."
            ),
            course_id=course_id,
        )

    return Recommendation(
        action="daily",
        summary=(
            f"Não há fila de erros em {course_title}. "
            "A sessão diária repete pouco do que já está estável e cobre o que ainda falta."
        ),
        course_id=course_id,
    )


def build_diagnosis(
    *,
    course_id: str,
    session_answers: list[dict],
    previous_accuracy: float | None,
    queue: list[ReviewItem],
    recommendation: Recommendation,
    warnings: list[str] | None = None,
) -> Diagnosis:
    total = len(session_answers)
    correct = sum(1 for row in session_answers if row["is_correct"])
    accuracy = (correct / total) if total else None
    errors = [row for row in session_answers if not row["is_correct"]]
    still = sorted({item.question_id for item in queue if item.active and item.reason == "error"})
    return Diagnosis(
        course_id=course_id,
        total=total,
        correct=correct,
        accuracy=accuracy,
        by_module=_bucket(session_answers, "module_id"),
        by_topic=_bucket(session_answers, "topic_id"),
        errors=errors,
        still_in_queue=still,
        comparison=compare_with_previous(accuracy, previous_accuracy),
        recommendation=recommendation,
        warnings=list(warnings or []),
    )

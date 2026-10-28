"""Relatório para colar noutro chat. Não inclui segredos."""

from __future__ import annotations

from study.core.diagnosis import Recommendation
from study.core.models import MasteryPolicy, TopicStats, learning_state


TUTOR_INSTRUCTION = (
    "Analisa os dados apresentados. Identifica os padrões de erro, separa dificuldades conceituais "
    "de erros ocasionais, propõe uma estratégia de estudo e gera uma lista de ações concretas. "
    "Prioriza os tópicos que ainda não estão dominados. Não recomendes repetir conteúdos que já estão "
    "estáveis sem uma justificação. Para o ambiente CNH, fundamenta as correções nas fontes normativas "
    "verificadas. Devolve um plano estruturado que possa ser aplicado à próxima sessão."
)


def render_markdown(
    *,
    course_title: str,
    course_id: str,
    exported_at: str,
    modules: list[dict],
    stats_by_topic: dict[str, TopicStats],
    pending_errors: list[dict],
    flagged: list[dict],
    recent_answers: list[dict],
    sessions: list[dict],
    recommendation: Recommendation,
    policy: MasteryPolicy,
    disclaimer: str,
) -> str:
    lines = [
        f"# Análise de estudo — {course_title}",
        "",
        f"- Curso: `{course_id}`",
        f"- Exportado em: {exported_at}",
        f"- Critério de domínio usado: {policy.threshold:.0%} e pelo menos {policy.min_evidence} tentativas, sem fila de erros ativa no tópico.",
        f"- Contexto: {disclaimer}",
        "",
        "## Módulos",
        "",
    ]
    mastered = []
    below = []
    for module in modules:
        status = module.get("lesson_status", "not_started")
        lines.append(f"### {module['title']}")
        lines.append(f"Lição: {status}. Questões no módulo: {module['question_count']}.")
        for topic in module["topics"]:
            stats = stats_by_topic.get(topic["id"], TopicStats(course_id, topic["id"]))
            pending = sum(1 for item in pending_errors if item["topic_id"] == topic["id"])
            state = learning_state(stats, pending, policy)
            accuracy = "sem tentativas" if stats.accuracy is None else f"{stats.accuracy:.0%}"
            lines.append(
                f"- {topic['name']} (`{topic['id']}`): {state}, {accuracy}, "
                f"{stats.attempts} tentativas, sequência de acertos {stats.consecutive_correct}, "
                f"fila de erros {pending}."
            )
            record = f"{topic['name']} ({accuracy}, {stats.attempts} tentativas)"
            if state == "dominado":
                mastered.append(record)
            elif state != "nao_estudado":
                below.append(record)
        lines.append("")

    lines.extend(["## Tópicos dominados", ""])
    lines.extend(f"- {item}" for item in mastered) if mastered else lines.append("- Nenhum tópico cumpre o critério gravado.")
    lines.extend(["", "## Tópicos abaixo do objetivo", ""])
    lines.extend(f"- {item}" for item in below) if below else lines.append("- Nenhum tópico estudado está abaixo do objetivo.")

    lines.extend(["", "## Questões erradas ainda relevantes", ""])
    if not pending_errors:
        lines.append("A fila de erros ativa está vazia.")
    for item in pending_errors:
        lines.append(
            f"- `{item['question_id']}` no tópico `{item['topic_id']}`, "
            f"acertos consecutivos na revisão: {item['consecutive_correct']}."
        )
        if item.get("question_text"):
            lines.append(f"  - Enunciado: {item['question_text']}")
        if item.get("chosen_answer") is not None:
            lines.append(f"  - Última resposta escolhida: {item['chosen_answer']}")
        if item.get("correct_answer"):
            lines.append(f"  - Resposta correta: {item['correct_answer']}")
        if item.get("explanation"):
            lines.append(f"  - Explicação: {item['explanation']}")

    lines.extend(["", "## Questões sinalizadas", ""])
    if not flagged:
        lines.append("Nenhuma questão sinalizada.")
    for item in flagged:
        lines.append(f"- `{item['question_id']}`")

    lines.extend(["", "## Respostas recentes", ""])
    if not recent_answers:
        lines.append("Ainda não há respostas gravadas.")
    for row in recent_answers[:40]:
        mark = "acertou" if row.get("is_correct") else "errou"
        lines.append(
            f"- {row.get('answered_at')}: {mark} `{row.get('question_id')}` "
            f"(tópico `{row.get('topic_id')}`). Escolheu «{row.get('chosen_answer')}». "
            f"Correta: «{row.get('correct_answer')}»."
        )

    lines.extend(["", "## Histórico resumido", ""])
    completed = [session for session in sessions if session.get("status") == "completed"]
    if not completed:
        lines.append("Nenhuma sessão concluída.")
    for session in completed[:8]:
        result = session.get("result") or {}
        accuracy = result.get("accuracy")
        label = "sem aproveitamento calculado" if accuracy is None else f"{accuracy:.0%}"
        lines.append(
            f"- Sessão {session['id']} ({session['kind']}) em {session.get('finished_at') or session['started_at']}: {label}."
        )

    lines.extend(
        [
            "",
            "## Recomendação do motor",
            "",
            recommendation.summary,
            "",
            "## Restrições para o próximo plano",
            "",
            "- Use apenas os números deste relatório. Não invente tentativas, percentagens nem erros.",
            "- Não trate uma questão de treino da CNH como enunciado oficial de prova.",
            "- Não misture o progresso de inglês com o da CNH.",
            "- Separe conteúdo confirmado por fonte de qualquer exemplo que você venha a criar.",
            "",
            "## Instrução para o tutor",
            "",
            TUTOR_INSTRUCTION,
            "",
        ]
    )
    return "\n".join(lines)

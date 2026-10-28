from __future__ import annotations

from datetime import date


def norm_warning(review_status: str, last_verified_at: str | None, *, today: date | None = None) -> str | None:
    """Aviso quando a regra da questão não está confirmada ou a verificação é antiga."""
    if review_status == "caderno":
        return None
    if review_status in {"pendente", "desatualizado"}:
        return "Esta questão depende de uma regra cuja vigência não foi confirmada."
    if not last_verified_at:
        return "Esta questão não tem data de verificação da fonte."
    today = today or date.today()
    try:
        verified = date.fromisoformat(last_verified_at[:10])
    except ValueError:
        return "A data de verificação desta questão é inválida."
    age = (today - verified).days
    if age > 365:
        return f"A fonte desta questão foi verificada há {age} dias e precisa de nova leitura."
    return None


def exam_rules_snapshot(config: dict) -> dict:
    distribution = config["distribution"]
    return {
        "question_count": config["questionCount"],
        "passing_score": config["passingScore"],
        "duration_minutes": config["durationMinutes"],
        "extended_duration_minutes": config["extendedDurationMinutes"],
        "options": config["optionsPerQuestion"],
        "distribution_official": distribution["official"],
        "distribution_label": distribution["label"],
        "modules": dict(distribution["modules"]),
    }


def validate_exam_config(config: dict) -> list[str]:
    problems: list[str] = []
    if config.get("questionCount") != 30:
        problems.append("O exame vigente tem 30 questões (Resolução CONTRAN 1.020/2025, art. 33, § 1º).")
    if config.get("passingScore") != 20:
        problems.append("A aprovação vigente exige 20 acertos (art. 34).")
    if config.get("durationMinutes") != 60:
        problems.append("A duração configurada deixou de ser o mínimo legal de 60 minutos (art. 33, § 2º).")
    if config.get("extendedDurationMinutes") != 120:
        problems.append("O tempo ampliado deve permanecer em 120 minutos.")
    if config.get("optionsPerQuestion") != 4:
        problems.append("Cada questão do exame tem quatro alternativas (art. 31).")
    modules = config.get("distribution", {}).get("modules", {})
    if sum(modules.values()) != config.get("questionCount"):
        problems.append("A soma da distribuição tem de ser igual ao número de questões.")
    if config.get("distribution", {}).get("official") is not False:
        problems.append("A distribuição por bloco não é oficial e não pode ser marcada como oficial.")
    return problems

from datetime import date, timedelta

from study.core.norms import norm_warning, validate_exam_config
from study.courses.cnh.loader import bank_gaps, load_cnh_catalog, load_exam_config
from study.reporting import TUTOR_INSTRUCTION, render_markdown
from study.core.diagnosis import Recommendation
from study.core.models import MasteryPolicy


def test_configuracao_oficial_do_simulado():
    config = load_exam_config()
    assert validate_exam_config(config) == []
    assert config["questionCount"] == 30
    assert config["passingScore"] == 20
    assert config["durationMinutes"] == 60
    assert config["extendedDurationMinutes"] == 120
    assert config["optionsPerQuestion"] == 4
    assert config["distribution"]["official"] is False
    assert sum(config["distribution"]["modules"].values()) == 30


def test_banco_cobre_o_simulado_e_declara_treino():
    catalog = load_cnh_catalog()
    assert bank_gaps(catalog) == []
    indexes = []
    for question in catalog.questions():
        if question.module_id == "procedimentos-al":
            continue
        assert len(question.choices) == 4
        assert all(choice.explanation for choice in question.choices)
        assert question.source and question.last_verified_at == "2026-10-27"
        assert question.origin == "treino"
        assert question.review_status == "verificado"
        indexes.append(question.correct_index)
    assert any(index != 0 for index in indexes)


def test_regra_nao_confirmada_gera_aviso():
    assert "não foi confirmada" in norm_warning("pendente", "2026-10-27")
    assert norm_warning("caderno", None) is None
    assert norm_warning("verificado", "2026-10-27", today=date(2026, 10, 27)) is None
    old = (date(2026, 10, 27) - timedelta(days=400)).isoformat()
    assert norm_warning("verificado", old, today=date(2026, 10, 27))


def test_relatorio_traz_a_instrucao_do_tutor():
    text = render_markdown(
        course_title="CNH — Alagoas",
        course_id="cnh-al",
        exported_at="2026-10-27T12:00:00-03:00",
        modules=[],
        stats_by_topic={},
        pending_errors=[],
        flagged=[],
        recent_answers=[],
        sessions=[],
        recommendation=Recommendation("lesson", "A lição de sinalização ainda não foi concluída.", "cnh-al"),
        policy=MasteryPolicy(),
        disclaimer="Preparação, não certificado.",
    )
    assert TUTOR_INSTRUCTION in text
    assert "A lição de sinalização ainda não foi concluída." in text

from datetime import datetime

from study.core.models import AnswerEvent
from study.persistence.exchange import apply_import, export_course, preview_import, strip_secrets, validate_payload
from study.persistence.store import Store


def _event(course, question, topic, correct, when):
    return AnswerEvent(
        course_id=course,
        question_id=question,
        topic_id=topic,
        module_id="modulo",
        chosen_answer="a" if correct else "b",
        correct_answer="a",
        is_correct=correct,
        mode="estudo",
        answered_at=when,
        question_text="Enunciado",
    )


def test_fila_persiste_e_reabre(tmp_path):
    path = tmp_path / "platform.db"
    store = Store(path)
    when = datetime(2026, 10, 27, 9, 0, 0)
    store.record_answer(_event("cnh-al", "q1", "pontos", False, when))
    store.record_answer(_event("cnh-al", "q1", "pontos", True, when))
    assert store.review_queue("cnh-al", active_only=True)[0].consecutive_correct == 1
    reopened = Store(path)
    reopened.record_answer(_event("cnh-al", "q1", "pontos", True, when))
    assert reopened.review_queue("cnh-al", active_only=True) == []
    kept = reopened.review_queue("cnh-al")
    assert kept[0].active is False
    assert len(reopened.answers("cnh-al")) == 3


def test_cursos_nao_partilham_estatistica(tmp_path):
    store = Store(tmp_path / "platform.db")
    when = datetime(2026, 10, 27, 9, 0, 0)
    store.record_answer(_event("english", "e1", "pontos", True, when))
    store.record_answer(_event("cnh-al", "c1", "pontos", False, when))
    assert store.topic_stats("english")["pontos"].correct == 1
    assert store.topic_stats("english")["pontos"].incorrect == 0
    assert store.topic_stats("cnh-al")["pontos"].incorrect == 1
    assert store.topic_stats("cnh-al")["pontos"].correct == 0


def test_exportacao_reimportacao_e_segredo(tmp_path):
    store = Store(tmp_path / "platform.db")
    when = datetime(2026, 10, 27, 9, 0, 0)
    store.record_answer(_event("english", "e1", "verbs-recall", False, when))
    store.record_answer(_event("cnh-al", "c1", "pontos", True, when))
    payload = export_course(store, "english", {"action": "review", "summary": "rever"}, when)
    payload["api_key"] = "nao-exportar"
    clean = strip_secrets(payload)
    assert "api_key" not in clean
    assert validate_payload(clean) == []
    preview = preview_import(clean)
    assert preview["answers"] == 1
    apply_import(store, clean)
    assert len(store.answers("english")) == 1
    assert store.topic_stats("cnh-al")["pontos"].correct == 1
    broken = dict(clean)
    broken["schemaVersion"] = 99
    assert validate_payload(broken)

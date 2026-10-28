from datetime import datetime

from study.courses.english.adapter import build_english_catalog
from study.courses.cnh.loader import load_exam_config
from study.persistence.store import Store
from study.services import Platform


def test_caderno_gera_questao_so_com_dados_gravados(tmp_path, monkeypatch):
    db = tmp_path / "word_bank.db"
    monkeypatch.setattr("word_bank.db.connection.DB_PATH", db)
    monkeypatch.setattr("word_bank.config.DEFAULT_XLSX", tmp_path / "ausente.xlsx")
    from word_bank.db import init_db
    from word_bank.repositories import word_bank as repo

    init_db()
    for word, meaning in (("small", "pequeno"), ("happy", "feliz"), ("tired", "cansado"), ("old", "velho")):
        repo.add_adjective({"english": word, "portuguese": meaning})
    catalog = build_english_catalog()
    questions = [question for question in catalog.questions() if question.module_id == "adjectives"]
    assert questions
    assert all(len(question.choices) == 4 for question in questions)
    assert all(question.origin == "caderno" for question in questions)
    assert all("caderno" in question.source.lower() or "word-bank" in question.source.lower() for question in questions)


def test_simulado_e_isolamento(tmp_path, monkeypatch):
    monkeypatch.setattr("word_bank.db.connection.DB_PATH", tmp_path / "word_bank.db")
    monkeypatch.setattr("word_bank.config.DEFAULT_XLSX", tmp_path / "ausente.xlsx")
    platform = Platform(Store(tmp_path / "platform.db"))
    config = load_exam_config()
    for module_id in config["distribution"]["modules"]:
        platform.set_lesson("cnh-al", module_id, "completed")
    session = platform.start_exam("cnh-al")
    assert len(session["question_ids"]) == 30
    assert session["config"]["duration_minutes"] == 60
    assert session["config"]["passing_score"] == 20
    platform.submit(session["id"], 0)
    result = platform.deliver_exam(session["id"])
    assert result["total"] == 30
    assert result["passed"] is False
    assert platform.store.topic_stats("english") == {}
    assert sum(item.attempts for item in platform.store.topic_stats("cnh-al").values()) == 30
    reopened = Platform(Store(tmp_path / "platform.db"))
    assert len(reopened.store.answers("cnh-al")) == 30
    assert reopened.store.sessions("cnh-al")[0]["status"] == "completed"

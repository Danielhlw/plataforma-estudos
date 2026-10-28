from datetime import datetime

from study.core.models import MasteryPolicy, QuestionRef, ReviewItem, TopicStats
from study.core.selection import select_daily, select_exam


def _question(qid, topic, module="m", importance=0):
    return QuestionRef(qid, topic, module, exam_importance=importance)


def test_nao_repete_questao_quando_ha_outra_do_mesmo_topico():
    questions = [_question("q1", "t"), _question("q2", "t")]
    picked = select_daily(
        questions,
        {"t": TopicStats("cnh-al", "t")},
        [],
        recent_question_ids=["q1"],
        count=1,
        now=datetime(2026, 10, 27),
        policy=MasteryPolicy(),
    )
    assert [item.question_id for item in picked] == ["q2"]


def test_erro_vem_antes_de_conteudo_ja_dominado():
    questions = [_question("erro", "fraco"), _question("velha", "ok")]
    stats = {
        "fraco": TopicStats("cnh-al", "fraco", attempts=5, correct=1),
        "ok": TopicStats("cnh-al", "ok", attempts=6, correct=6),
    }
    queue = [ReviewItem("cnh-al", "erro", "fraco", active=True, entered_at="2026-10-27T10:00:00")]
    picked = select_daily(
        questions,
        stats,
        queue,
        [],
        count=1,
        now=datetime(2026, 10, 27, 12, 0, 0),
        policy=MasteryPolicy(),
    )
    assert picked[0].question_id == "erro"


def test_simulado_recusa_bloco_incompleto():
    questions = [_question("a", "t", "sinalizacao")]
    try:
        select_exam(questions, {"sinalizacao": 2})
    except ValueError as exc:
        assert "sinalizacao" in str(exc)
    else:
        raise AssertionError("deveria faltar questão")

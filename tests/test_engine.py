from datetime import datetime

from study.core.engine import apply_answer
from study.core.models import MasteryPolicy, ReviewItem, TopicStats, is_mastered


def test_dois_acertos_consecutivos_esvaziam_a_fila_sem_apagar_o_item():
    policy = MasteryPolicy()
    stats = TopicStats("cnh-al", "pontos")
    now = datetime(2026, 10, 27, 12, 0, 0)
    first = apply_answer(stats, None, correct=False, question_id="q1", now=now, policy=policy)
    assert first.review is not None and first.review.active
    assert first.review.consecutive_correct == 0

    second = apply_answer(first.stats, first.review, correct=True, question_id="q1", now=now, policy=policy)
    assert second.review.active
    assert second.review.consecutive_correct == 1
    assert second.cleared_review is False

    third = apply_answer(second.stats, second.review, correct=True, question_id="q1", now=now, policy=policy)
    assert third.review.active is False
    assert third.review.consecutive_correct == 2
    assert third.review.entered_at == first.review.entered_at


def test_erro_reinicia_a_sequencia():
    policy = MasteryPolicy()
    stats = TopicStats("english", "verbs-recall", attempts=2, correct=2, consecutive_correct=2)
    review = ReviewItem("english", "q1", "verbs-recall", consecutive_correct=1, active=True, entered_at="2026-10-01")
    applied = apply_answer(stats, review, correct=False, question_id="q1", now=datetime(2026, 10, 27), policy=policy)
    assert applied.stats.consecutive_correct == 0
    assert applied.review.consecutive_correct == 0
    assert applied.review.active


def test_percentagem_sem_evidencia_minima_nao_domina():
    policy = MasteryPolicy(min_evidence=5)
    stats = TopicStats("cnh-al", "pontos", attempts=4, correct=4, consecutive_correct=4)
    assert is_mastered(stats, 0, policy) is False
    stats.attempts = 5
    stats.correct = 4
    assert is_mastered(stats, 0, policy)
    assert is_mastered(stats, 1, policy) is False

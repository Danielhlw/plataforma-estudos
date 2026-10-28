from __future__ import annotations

import html

import streamlit as st

from study.services import LessonRequired, Platform
from study.persistence.store import StoreError
from study.ui.theme import STATE_LABELS


def render_practice(platform: Platform, course_id: str) -> None:
    if "last_result" in st.session_state:
        _result(platform, st.session_state["last_result"])
        return

    session = platform.store.active_session(course_id)
    if session is None:
        st.info("Não há sessão em andamento neste curso.")
        if st.button("Iniciar sessão diária", type="primary"):
            _run(platform.start_daily, course_id)
        return

    remaining = platform.remaining_seconds(session)
    if session["kind"] == "simulado" and remaining == 0:
        _finish_exam(platform, session["id"])
        return

    catalog = platform.catalog(course_id)
    total = len(session["question_ids"])
    index = min(session["current_index"], total)
    feedback = st.session_state.get("feedback")
    showing_feedback = bool(
        feedback
        and feedback.get("session_id") == session["id"]
        and session["config"].get("reveal", True)
    )
    answered_number = index if showing_feedback else index + 1
    answered_so_far = max(0, index - (1 if showing_feedback else 0))
    st.progress(answered_so_far / total if total else 0)
    header = f"{session['kind'].capitalize()} · questão {min(max(answered_number, 1), total)} de {total}"
    if remaining is not None:
        header += f" · {remaining // 60:02d}:{remaining % 60:02d}"
    st.subheader(header)
    if session["kind"] == "simulado":
        st.caption("As respostas e o gabarito aparecem só no fim. O tempo é o mínimo legal configurado, não um certificado do DETRAN.")

    feedback = st.session_state.get("feedback")
    if feedback and feedback.get("session_id") == session["id"] and session["config"].get("reveal", True):
        _feedback(platform, session, feedback)
        return

    if index >= total:
        if session["kind"] == "simulado":
            if st.button("Entregar prova", type="primary"):
                _finish_exam(platform, session["id"])
        else:
            st.info("Esta sessão já foi respondida.")
        return

    question = catalog.get(session["question_ids"][index])
    if question is None:
        st.error("A questão saiu do conteúdo. Abandone a sessão e comece outra.")
        return
    from study.core.norms import norm_warning

    warning = norm_warning(question.review_status, question.last_verified_at)
    if warning:
        st.markdown(f'<div class="warn-box">{warning}</div>', unsafe_allow_html=True)
    if question.origin == "treino":
        st.caption("Questão de treino, não é enunciado oficial de prova.")
    st.markdown(f'<p class="prompt">{html.escape(question.prompt)}</p>', unsafe_allow_html=True)
    labels = [choice.text for choice in question.choices]
    choice = st.radio("Alternativas", options=list(range(len(labels))), format_func=lambda i: labels[i], key=f"choice-{session['id']}-{index}")
    cols = st.columns(3)
    with cols[0]:
        if st.button("Responder", type="primary", use_container_width=True):
            try:
                outcome = platform.submit(session["id"], int(choice))
            except StoreError as exc:
                st.error(str(exc))
                return
            if outcome.get("finished"):
                st.session_state["last_result"] = outcome["finished"]
                st.session_state.pop("feedback", None)
                st.rerun()
            if outcome.get("awaiting_delivery") or not session["config"].get("reveal", True):
                st.session_state.pop("feedback", None)
                st.rerun()
            outcome["feedback"]["session_id"] = session["id"]
            st.session_state["feedback"] = outcome["feedback"]
            st.rerun()
    with cols[1]:
        flagged = platform.store.is_flagged(course_id, question.id)
        if st.button("Tirar sinalização" if flagged else "Sinalizar para revisão", use_container_width=True):
            platform.toggle_flag(course_id, question.id, question.topic_id)
            st.rerun()
    with cols[2]:
        if st.button("Abandonar sessão", use_container_width=True):
            st.session_state["confirm_abandon"] = session["id"]
    if session["kind"] == "simulado" and st.button("Entregar prova agora"):
        st.session_state["confirm_deliver"] = session["id"]
    if st.session_state.get("confirm_deliver") == session["id"]:
        st.warning("Questões sem resposta contam como erro. A entrega grava o resultado.")
        if st.button("Confirmar entrega"):
            st.session_state.pop("confirm_deliver", None)
            _finish_exam(platform, session["id"])
            return
    if st.session_state.get("confirm_abandon") == session["id"]:
        st.warning("Abandonar não apaga respostas já gravadas no modo estudo. No simulado, as respostas só entram nas estatísticas quando a prova é entregue.")
        if st.button("Confirmar abandono"):
            platform.abandon(session["id"])
            st.session_state.pop("confirm_abandon", None)
            st.session_state.pop("feedback", None)
            st.rerun()


def _feedback(platform: Platform, session: dict, feedback: dict) -> None:
    ok = feedback["is_correct"]
    css = "feedback-ok" if ok else "feedback-bad"
    title = "Correta" if ok else "Incorreta"
    st.markdown(f'<div class="{css}"><strong>{title}.</strong> Você escolheu: {feedback["chosen_answer"]}</div>', unsafe_allow_html=True)
    if feedback.get("warning"):
        st.markdown(f'<div class="warn-box">{feedback["warning"]}</div>', unsafe_allow_html=True)
    st.markdown("**Por que cada alternativa**")
    for item in feedback["explanations"]:
        mark = "Correta" if item["correct"] else "Incorreta"
        st.markdown(f"- **{mark} — {item['text']}** {item['explanation']}")
    st.markdown(f"**Como reconhecer este padrão.** {feedback['recognition_key']}")
    if feedback.get("source"):
        st.caption(f"Fonte: {feedback['source']}")
    if session["course_id"] == "english":
        sentence = st.text_area("Escreva uma frase com o que acabou de estudar. Ela fica guardada e não é corrigida automaticamente.")
        if st.button("Guardar frase para eu rever depois"):
            try:
                platform.save_sentence(session["id"], feedback["question_id"], sentence)
                platform.store.set_flag(session["course_id"], feedback["question_id"], feedback["topic_id"], True, platform.now())
                st.success("Frase guardada. A palavra foi sinalizada. Isso não conta como acerto nem como erro de questão.")
            except StoreError as exc:
                st.error(str(exc))
    if st.button("Continuar", type="primary"):
        st.session_state.pop("feedback", None)
        st.rerun()


def _finish_exam(platform: Platform, session_id: int) -> None:
    try:
        st.session_state["last_result"] = platform.deliver_exam(session_id)
        st.session_state.pop("feedback", None)
        st.rerun()
    except StoreError as exc:
        st.error(str(exc))


def _result(platform: Platform, result: dict) -> None:
    st.subheader("Resultado da sessão")
    st.write(result["score_label"])
    if result.get("accuracy") is not None:
        st.write(f"Aproveitamento: {result['accuracy']:.0%}")
    if "passed" in result:
        passing = result["passing_score"]
        if result["passed"]:
            st.markdown(f'<div class="feedback-ok">Atingiu o critério configurado de {passing} acertos. Isto não é aprovação no DETRAN.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-bad">Não atingiu {passing} acertos. Questão não respondida conta como erro.</div>', unsafe_allow_html=True)
        rules = result.get("official_format") or {}
        if rules and rules.get("distribution_official") is False:
            st.caption(rules.get("distribution_label", "A distribuição por tema deste simulado não é oficial."))
    st.write(result["comparison"])
    st.write(f"Próximo passo: {result['recommendation']}")
    if result.get("warnings"):
        st.warning("Há questões desta sessão com fonte não confirmada ou verificação antiga.")
    if result["by_topic"]:
        rows = []
        for topic_id, bucket in result["by_topic"].items():
            accuracy = bucket["accuracy"]
            rows.append({"Tópico": topic_id, "Acertos": bucket["correct"], "Total": bucket["total"], "Aproveitamento": "—" if accuracy is None else f"{accuracy:.0%}"})
        st.dataframe(rows, use_container_width=True, hide_index=True)
    if result["still_in_queue"]:
        st.markdown("**Ainda na fila de erros**")
        for question_id in result["still_in_queue"]:
            st.write(f"- `{question_id}`")
    with st.expander("Gabarito comentado"):
        for answer in result.get("answers") or []:
            mark = "Correta" if answer["is_correct"] else "Incorreta"
            st.markdown(f"**{mark}.** {answer['question_text']}")
            st.caption(f"Escolhida: {answer['chosen_answer']} · Correta: {answer['correct_answer']}")
            for item in answer.get("explanations") or []:
                st.write(f"- {item['text']}: {item['explanation']}")
            if answer.get("recognition_key"):
                st.markdown(f"**Como reconhecer este padrão.** {answer['recognition_key']}")
    if st.button("Voltar"):
        st.session_state.pop("last_result", None)
        st.rerun()


def _run(callback, *args) -> None:
    try:
        callback(*args)
        st.rerun()
    except LessonRequired as exc:
        st.warning(str(exc) + " Abra a lição antes. Dispensar fica registado.")
        st.session_state["lesson_module"] = exc.module_id
    except StoreError as exc:
        st.error(str(exc))

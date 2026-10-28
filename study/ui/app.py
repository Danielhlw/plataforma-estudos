"""Interface da plataforma."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from study.paths import PLATFORM_DB
from study.persistence.exchange import ImportError
from study.persistence.store import Store, StoreError
from study.services import LessonRequired, Platform
from study.ui.practice import render_practice
from study.ui.theme import STATE_LABELS, install_theme, minutes, page_title

PRIMARY = [
    ("overview", "Início", ":material/home:"),
    ("today", "Hoje", ":material/today:"),
    ("modules", "Módulos", ":material/menu_book:"),
    ("review", "Revisão", ":material/replay:"),
    ("cards", "Cartões", ":material/style:"),
]
SECONDARY = [
    ("stats", "Progresso", ":material/bar_chart:"),
    ("history", "Histórico", ":material/history:"),
    ("export", "Exportar", ":material/ios_share:"),
    ("settings", "Ajustes", ":material/settings:"),
]


def main() -> None:
    st.set_page_config(page_title="Estudos", page_icon="📚", layout="wide", initial_sidebar_state="expanded")
    install_theme()
    platform = Platform(Store(PLATFORM_DB))
    if "pending_nav" in st.session_state:
        st.session_state["nav"] = st.session_state.pop("pending_nav")
    if "nav" not in st.session_state:
        st.session_state["nav"] = "overview"

    with st.sidebar:
        st.markdown(
            '<div class="brand-row"><div class="brand-mark">E</div><p class="brand">Estudos</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="switch-anchor"></div>', unsafe_allow_html=True)
        _course_switch(platform)
        st.markdown('<p class="nav-label">Estudar</p>', unsafe_allow_html=True)
        for key, label, icon in PRIMARY:
            _nav_button(platform, key, label, icon)
        st.markdown('<p class="nav-label">Conta</p>', unsafe_allow_html=True)
        for key, label, icon in SECONDARY:
            _nav_button(platform, key, label, icon)
        course = platform.active_course()
        active = platform.store.active_session(course)
        if active:
            st.caption(f"{active['kind'].capitalize()} em andamento · questão {active['current_index'] + 1}")

    page = st.session_state["nav"]
    if page == "modules":
        page = "cnh" if platform.active_course() == "cnh-al" else "english"
        st.session_state["nav"] = page

    try:
        if page == "overview":
            _overview(platform)
        elif page == "english":
            _course(platform, "english")
        elif page == "cnh":
            _course(platform, "cnh-al")
        elif page == "today":
            _today(platform)
        elif page == "review":
            _review(platform)
        elif page == "cards":
            _cards(platform)
        elif page == "stats":
            _stats(platform)
        elif page == "history":
            _history(platform)
        elif page == "export":
            _export(platform)
        else:
            _settings(platform)
    except StoreError as exc:
        st.error(str(exc))


def goto(page: str) -> None:
    st.session_state["pending_nav"] = page
    st.rerun()


def _slot(nav: str) -> str:
    if nav in {"english", "cnh"}:
        return "modules"
    return nav


def _target(platform: Platform, key: str) -> str:
    if key == "modules":
        return "cnh" if platform.active_course() == "cnh-al" else "english"
    return key


def _nav_button(platform: Platform, key: str, label: str, icon: str) -> None:
    current = _slot(st.session_state.get("nav", "overview"))
    if st.button(
        label,
        key=f"nav-{key}",
        type="primary" if current == key else "secondary",
        icon=icon,
        width="stretch",
    ):
        dest = _target(platform, key)
        if st.session_state.get("nav") != dest:
            goto(dest)


def _course_switch(platform: Platform) -> None:
    course = platform.active_course()
    left, right = st.columns(2)
    with left:
        if st.button("Inglês", key="switch-en", type="primary" if course == "english" else "secondary", use_container_width=True):
            _switch_course(platform, "english")
    with right:
        if st.button("CNH", key="switch-cnh", type="primary" if course == "cnh-al" else "secondary", use_container_width=True):
            _switch_course(platform, "cnh-al")


def _switch_course(platform: Platform, course_id: str) -> None:
    if platform.active_course() == course_id:
        return
    platform.set_active_course(course_id)
    if st.session_state.get("nav") in {"english", "cnh"}:
        goto("cnh" if course_id == "cnh-al" else "english")
    st.rerun()


def _overview(platform: Platform) -> None:
    active_id = platform.active_course()
    active = platform.course_view(active_id)
    english = platform.course_view("english")
    cnh = platform.course_view("cnh-al")
    main, rail = st.columns([2.35, 1], gap="large")
    with main:
        st.markdown(
            f"""
            <div class="hero">
                <div class="kicker">CURSO ATIVO</div>
                <h2>{html.escape(active["catalog"].title)}</h2>
                <p>{html.escape(active["recommendation"].summary)}</p>
            </div>
            <div class="chip-row">
                <div class="chip"><b>{active["mastered"]}/{active["topic_count"]}</b><span>tópicos dominados</span></div>
                <div class="chip"><b>{len(active["pending"])}</b><span>na fila de erros</span></div>
                <div class="chip"><b>{minutes(active["seconds"])}</b><span>de estudo</span></div>
            </div>
            <div class="section-label">Seus cursos</div>
            """,
            unsafe_allow_html=True,
        )
        left, right = st.columns(2, gap="medium")
        with left:
            _course_tile(platform, "english", english)
        with right:
            _course_tile(platform, "cnh-al", cnh)
    with rail:
        _progress_rail(active)


def _course_tile(platform: Platform, course_id: str, view: dict) -> None:
    kind = "cnh" if course_id == "cnh-al" else "english"
    with st.container(border=True):
        st.markdown(
            f'<div class="tile-art {kind}"><span>{html.escape(view["catalog"].title)}</span></div>'
            f'<p class="tile-copy">{html.escape(view["recommendation"].summary)}</p>',
            unsafe_allow_html=True,
        )
        if view["active_session"]:
            if st.button("Continuar", key=f"go-{course_id}", type="primary", width="stretch"):
                platform.set_active_course(course_id)
                goto("today")
        elif st.button("Sessão de hoje", key=f"daily-{course_id}", type="primary", width="stretch"):
            platform.set_active_course(course_id)
            _start(platform.start_daily, course_id)


def _progress_rail(view: dict) -> None:
    hour = datetime.now().astimezone().hour
    if hour < 12:
        hello = "Bom dia"
    elif hour < 18:
        hello = "Boa tarde"
    else:
        hello = "Boa noite"
    by_module: dict[str, int] = {}
    for topic in view["topics"]:
        by_module[topic["module_title"]] = by_module.get(topic["module_title"], 0) + topic["attempts"]
    peak = max(by_module.values(), default=0) or 1
    heights = [18 + int(68 * count / peak) if count else 14 for count in by_module.values()] or [14]
    bars = "".join(f'<i style="height:{height}px"></i>' for height in heights)
    streak = view["streak"]
    streak_label = "1 dia" if streak == 1 else f"{streak} dias"
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="rail">
                <div class="hello">{hello}</div>
                <h3>Seu progresso</h3>
                <div class="bar-chart" title="Acerto médio por módulo">{bars}</div>
                <div class="rail-stat"><span>Sequência</span><b>{streak_label}</b></div>
                <div class="rail-stat"><span>Tempo</span><b>{minutes(view["seconds"])}</b></div>
                <div class="rail-stat"><span>Fila</span><b>{len(view["pending"])}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _course(platform: Platform, course_id: str) -> None:
    view = platform.course_view(course_id)
    page_title(view["catalog"].title, view["catalog"].disclaimer)
    if view["norm_warnings"]:
        st.warning(f"{len(view['norm_warnings'])} questão(ões) com fonte por confirmar.")
    if view["exam_gaps"]:
        st.warning("Simulado indisponível. " + " ".join(view["exam_gaps"]))
    if view["active_session"]:
        st.info(f"Sessão de {view['active_session']['kind']} em andamento.")
        if st.button("Continuar sessão"):
            goto("today")
    if course_id == "english":
        modules_tab, book_tab = st.tabs(["Módulos", "Caderno"])
        with modules_tab:
            _modules(platform, course_id, view)
        with book_tab:
            _notebook()
    else:
        _modules(platform, course_id, view)
        if st.button("Simulado de 30 questões", type="primary"):
            _start(platform.start_exam, course_id)


def _modules(platform: Platform, course_id: str, view: dict) -> None:
    modules = view["catalog"].modules
    labels = {}
    for module in modules:
        status = view["lessons"].get(module.id, "not_started")
        labels[module.id] = f"{module.title} · {_lesson_label(status)}"
    selected = st.selectbox("Módulo", options=[module.id for module in modules], format_func=lambda item: labels[item])
    module = next(item for item in modules if item.id == selected)
    status = view["lessons"].get(module.id, "not_started")
    with st.container(border=True):
        st.write(module.summary)
        if module.official_block:
            st.caption(module.official_block)
        st.caption(f"{module.question_count} questões")
        practice, done = st.columns(2)
        with practice:
            if st.button("Praticar", key=f"practice-{course_id}-{module.id}", type="primary", use_container_width=True):
                _start(platform.start_study, course_id, module.id)
        with done:
            if st.button("Concluí a lição", key=f"done-{course_id}-{module.id}", use_container_width=True):
                platform.set_lesson(course_id, module.id, "completed")
                st.rerun()
        if st.button("Dispensar lição", key=f"skip-{course_id}-{module.id}"):
            st.session_state[f"skip-{module.id}"] = True
        if st.session_state.get(f"skip-{module.id}"):
            st.warning("Avançar sem estudar pode prejudicar a aprendizagem. A dispensa fica registada.")
            if st.button("Registar dispensa", key=f"confirm-skip-{module.id}"):
                platform.set_lesson(course_id, module.id, "skipped")
                st.session_state.pop(f"skip-{module.id}", None)
                st.rerun()
    with st.expander("Lição", expanded=status == "not_started"):
        _lesson_body(module)


def _lesson_body(module) -> None:
    lesson = module.topics[0].lesson if module.topics else None
    if lesson is None:
        st.write("Este módulo ainda não tem lição.")
        return
    for block in lesson.blocks:
        st.write(block)
    if lesson.concepts:
        st.markdown("**Conceitos**")
        for item in lesson.concepts:
            st.write(f"- {item}")
    if lesson.examples:
        st.markdown("**Exemplos**")
        for item in lesson.examples:
            st.write(f"- {item}")
    if lesson.comparisons:
        rows = [
            {"De um lado": row.get("left", ""), "Do outro": row.get("right", ""), "O que muda": row.get("difference", "")}
            for row in lesson.comparisons
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    for title, items in (
        ("Relações", lesson.relations),
        ("Como reconhecer no enunciado", lesson.rules),
        ("Erros comuns", lesson.pitfalls),
        ("Para memorizar", lesson.memorize),
    ):
        if items:
            st.markdown(f"**{title}**")
            for item in items:
                st.write(f"- {item}")
    if lesson.sources:
        st.caption("Fontes: " + " · ".join(source["title"] for source in lesson.sources))


def _today(platform: Platform) -> None:
    course_id = platform.active_course()
    if platform.store.active_session(course_id) is not None or "last_result" in st.session_state:
        render_practice(platform, course_id)
        return
    page_title("Hoje", platform.recommendation(course_id).summary)
    if st.button("Começar", type="primary"):
        _start(platform.start_daily, course_id)


def _review(platform: Platform) -> None:
    course_id = platform.active_course()
    if platform.store.active_session(course_id):
        render_practice(platform, course_id)
        return
    page_title("Revisão", "A fila só esvazia com dois acertos seguidos.")
    view = platform.course_view(course_id)
    mode = st.radio(
        "O que rever",
        options=["errors", "flagged", "topic"],
        format_func=lambda item: {"errors": "Fila de erros", "flagged": "Sinalizadas", "topic": "Um tópico"}[item],
        horizontal=True,
    )
    topic_id = None
    if mode == "topic":
        options = {topic["name"]: topic["topic_id"] for topic in view["topics"]}
        if not options:
            st.info("Ainda não há tópicos com questões.")
            return
        topic_id = options[st.selectbox("Tópico", list(options))]
    if st.button("Começar", type="primary"):
        _start(platform.start_review, course_id, mode, topic_id)


def _cards(platform: Platform) -> None:
    course_id = platform.active_course()
    catalog = platform.catalog(course_id)
    cards = [card for module in catalog.modules for topic in module.topics for card in topic.flashcards]
    page_title("Cartões")
    if not cards:
        st.info("Não há cartões. No inglês, eles nascem dos registos do caderno.")
        return
    progress = platform.store.flashcards(course_id)
    now = platform.now().isoformat(timespec="seconds")
    due = [card for card in cards if progress.get(card.id) is None or (progress[card.id].due_at or "") <= now]
    st.caption(f"{len(due)} para ver agora, de {len(cards)}.")
    card = (due or cards)[st.session_state.get("card_cursor", 0) % len(due or cards)]
    with st.container(border=True):
        st.markdown(f'<p class="prompt">{html.escape(card.front)}</p>', unsafe_allow_html=True)
        if st.session_state.get("card_show") == card.id:
            st.write(card.back)
            if card.source:
                st.caption(card.source)
            cols = st.columns(4)
            for column, grade, label in zip(cols, ("again", "hard", "good", "easy"), ("De novo", "Difícil", "Bom", "Fácil")):
                with column:
                    if st.button(label, use_container_width=True, type="primary" if grade == "good" else "secondary"):
                        platform.grade_card(course_id, card.id, grade)
                        st.session_state["card_show"] = None
                        st.session_state["card_cursor"] = st.session_state.get("card_cursor", 0) + 1
                        st.rerun()
        elif st.button("Mostrar resposta", type="primary"):
            st.session_state["card_show"] = card.id
            st.rerun()


def _stats(platform: Platform) -> None:
    course_id = platform.active_course()
    view = platform.course_view(course_id)
    page_title("Progresso")
    if not view["topics"]:
        st.info("Ainda não há tópicos com questões para medir.")
        return
    frame = pd.DataFrame(
        [
            {
                "Tópico": topic["name"],
                "Estado": STATE_LABELS[topic["state"]],
                "Tentativas": topic["attempts"],
                "Acertos": topic["correct"],
                "Erros": topic["incorrect"],
                "Aproveitamento": None if topic["accuracy"] is None else round(topic["accuracy"] * 100),
                "Sequência": topic["consecutive_correct"] or 0,
                "Fila": topic["pending"],
            }
            for topic in view["topics"]
            if topic["attempts"]
        ]
    )
    if frame.empty:
        st.info("Ainda não há tentativas neste curso.")
        return
    st.dataframe(frame, use_container_width=True, hide_index=True)
    chart = frame.dropna(subset=["Aproveitamento"])
    if not chart.empty:
        st.bar_chart(chart, x="Tópico", y="Aproveitamento")
    resting = view["topic_count"] - len(frame)
    if resting:
        st.caption(f"{resting} tópicos ainda sem tentativas.")


def _history(platform: Platform) -> None:
    course_id = platform.active_course()
    page_title("Histórico")
    sessions = platform.store.sessions(course_id)
    if not sessions:
        st.info("Nenhuma sessão gravada neste curso.")
        return
    for session in sessions[:12]:
        result = session.get("result") or {}
        accuracy = result.get("accuracy")
        label = _status_label(session["status"]) if accuracy is None else f"{accuracy:.0%}"
        with st.expander(f"{_when(session['started_at'])} · {session['kind']} · {label}"):
            if result:
                st.write(result.get("comparison"))
                st.write(result.get("recommendation"))
            else:
                st.write(f"Estado: {_status_label(session['status'])}")


def _export(platform: Platform) -> None:
    page_title("Exportar", "O ficheiro não leva chaves, tokens nem senhas. Não há modelo ligado aqui.")
    course_id = st.selectbox("Curso", options=["english", "cnh-al"], format_func=lambda item: "Inglês" if item == "english" else "CNH — Alagoas")
    json_text = platform.export_json(course_id)
    markdown = platform.export_markdown(course_id)
    left, right = st.columns(2)
    with left:
        st.download_button("JSON", data=json_text, file_name=f"{course_id}-progresso.json", mime="application/json", use_container_width=True)
    with right:
        st.download_button("Markdown", data=markdown, file_name=f"{course_id}-analise.md", mime="text/markdown", use_container_width=True)
    with st.expander("Preparar análise com IA"):
        st.text_area("Relatório para copiar", markdown, height=240, label_visibility="collapsed")
    upload = st.file_uploader("Importar um JSON exportado antes", type=["json"])
    if upload is not None:
        text = upload.getvalue().decode("utf-8")
        try:
            preview = platform.preview(text)
        except ImportError as exc:
            st.error(str(exc))
            return
        st.write(
            f"Curso {preview['course']}, exportado em {preview['exportedAt']}: "
            f"{preview['answers']} respostas, {preview['sessions']} sessões, {preview['reviewQueue']} itens de fila."
        )
        st.warning("Confirmar substitui o progresso deste curso. O outro curso não é alterado.")
        agree = st.checkbox("Quero substituir o progresso deste curso pelos dados do ficheiro.")
        if agree and st.button("Importar e substituir"):
            try:
                platform.restore(text)
                st.success("Progresso substituído.")
            except ImportError as exc:
                st.error(str(exc))


def _settings(platform: Platform) -> None:
    page_title("Ajustes")
    count = st.number_input("Questões da sessão diária", min_value=10, max_value=15, value=int(platform.store.get_setting("daily_question_count")))
    evidence = st.number_input("Mínimo de tentativas para domínio", min_value=2, max_value=30, value=int(platform.store.get_setting("min_evidence")))
    threshold = st.slider("Aproveitamento mínimo para domínio", min_value=0.5, max_value=1.0, value=float(platform.store.get_setting("mastery_threshold")), step=0.05)
    extended = st.checkbox("Tempo ampliado no simulado (120 minutos)", value=platform.store.get_setting("exam_extended_time") == "1")
    if st.button("Guardar", type="primary"):
        try:
            platform.store.set_setting("daily_question_count", str(int(count)))
            platform.store.set_setting("min_evidence", str(int(evidence)))
            platform.store.set_setting("mastery_threshold", str(float(threshold)))
            platform.store.set_setting("exam_extended_time", "1" if extended else "0")
            platform.policy()
            st.success("Configurações guardadas.")
        except (StoreError, ValueError) as exc:
            st.error(str(exc))
    st.caption("A fila continua a sair só com dois acertos consecutivos.")


def _notebook() -> None:
    from word_bank.ui.app import VIEWS, _bootstrap_data

    _bootstrap_data()
    section = st.selectbox(
        "Secção do caderno",
        options=list(VIEWS),
        format_func=lambda key: {
            "verbs": "Verbos",
            "adjectives": "Adjetivos",
            "nouns": "Substantivos",
            "tense": "Tempos",
            "yesno": "Yes/No",
            "revision": "Revisão do BE",
        }[key],
    )
    VIEWS[section]()


def _lesson_label(status: str) -> str:
    return {"completed": "concluída", "skipped": "dispensada", "not_started": "por fazer"}.get(status, status)


def _status_label(status: str) -> str:
    return {"in_progress": "em andamento", "completed": "concluída", "abandoned": "abandonada"}.get(status, status)


def _when(value: str) -> str:
    text = value.replace("T", " ")[:16]
    date, clock = text.split(" ")
    year, month, day = date.split("-")
    return f"{day}/{month}/{year} · {clock}"


def _start(callback, *args) -> None:
    try:
        callback(*args)
        st.session_state.pop("feedback", None)
        st.session_state.pop("last_result", None)
        goto("today")
    except LessonRequired as exc:
        st.warning(str(exc) + " Conclua a lição ou registe a dispensa. A dispensa fica gravada.")
    except StoreError as exc:
        st.error(str(exc))

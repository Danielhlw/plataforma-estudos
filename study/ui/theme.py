import streamlit as st


def install_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --ink: #241b3a;
            --muted: #8d89a3;
            --line: #eeeaf6;
            --paper: #ffffff;
            --canvas: #eef0f6;
            --violet: #6d35e8;
            --violet-deep: #5b21d6;
            --violet-soft: #f4efff;
            --radius: 22px;
        }

        html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea, label {
            font-family: Manrope, sans-serif;
        }
        .stApp { background: var(--canvas); color: var(--ink); }

        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {
            display: none;
        }

        [data-testid="stSidebar"] {
            background: var(--paper) !important;
            border-right: none;
        }
        [data-testid="stMain"] .block-container {
            background: var(--paper);
            border-radius: 28px;
            min-height: calc(100vh - 36px);
            margin: 18px 18px 18px 6px;
            box-shadow: 0 10px 36px rgba(48, 24, 96, 0.06);
        }
        [data-testid="stSidebar"] * { color: var(--ink); }
        [data-testid="stSidebarContent"] { padding-top: 1.2rem; }

        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
            background: transparent;
            border: none;
            box-shadow: none;
            justify-content: flex-start;
            padding-left: 0.7rem;
            border-radius: 12px;
            font-weight: 600;
            color: #6f6b86 !important;
        }
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
            color: var(--violet) !important;
            background: var(--violet-soft);
        }
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
            background: #f7f4ff;
            color: var(--violet) !important;
        }
        [data-testid="stSidebar"] .stButton > button { min-height: 2.4rem; }

        .block-container {
            padding: 1.35rem 1.45rem 2.4rem;
            max-width: none;
        }
        [data-testid="stSidebar"] .stElementContainer:has(.switch-anchor) + [data-testid="stLayoutWrapper"] button {
            background: #f3f0fa !important;
            color: #5c5678 !important;
            border-radius: 999px !important;
            font-weight: 700;
        }
        [data-testid="stSidebar"] .stElementContainer:has(.switch-anchor) + [data-testid="stLayoutWrapper"] [data-testid="stBaseButton-primary"] {
            background: var(--violet) !important;
            color: white !important;
        }

        .brand-row { display: flex; align-items: center; gap: 0.65rem; margin: 0 0 1rem; }
        .brand-mark {
            width: 36px; height: 36px; border-radius: 999px;
            background: var(--violet); color: white !important;
            display: flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 1rem;
        }
        .brand { font-weight: 800; font-size: 1.05rem; letter-spacing: -0.03em; margin: 0; }
        .nav-label {
            margin: 1.1rem 0 0.25rem;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #b0adc2 !important;
        }
        .page-title {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin: 0 0 0.2rem;
        }
        .lede, .quiet-note { color: var(--muted) !important; font-size: 0.95rem; line-height: 1.45; }
        .prompt { font-size: 1.15rem; line-height: 1.5; font-weight: 650; margin: 0.35rem 0 0.8rem; }

        .hero {
            background: linear-gradient(115deg, #6428e0 0%, #7c3aed 48%, #9b6bff 100%);
            border-radius: 24px;
            padding: 1.45rem 1.5rem 1.25rem;
            min-height: 148px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 16px 40px rgba(109, 53, 232, 0.22);
        }
        .hero::before, .hero::after {
            content: "";
            position: absolute;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
        }
        .hero::before { width: 140px; height: 140px; right: 28px; top: -46px; }
        .hero::after { width: 90px; height: 90px; right: 120px; bottom: -36px; }
        .hero .kicker {
            position: relative; z-index: 1;
            color: rgba(255,255,255,0.82) !important;
            font-size: 0.68rem; font-weight: 800; letter-spacing: 0.14em;
        }
        .hero h2 {
            position: relative; z-index: 1;
            color: white !important;
            font-size: 1.65rem; font-weight: 800; letter-spacing: -0.03em;
            margin: 0.3rem 0 0.35rem;
        }
        .hero p {
            position: relative; z-index: 1;
            color: rgba(255,255,255,0.92) !important;
            margin: 0; max-width: 38rem; line-height: 1.4;
        }

        .chip-row { display: flex; gap: 0.75rem; margin: 0.9rem 0 1.2rem; }
        .chip {
            flex: 1;
            background: #f7f5fc;
            border-radius: 16px;
            padding: 0.75rem 0.85rem;
        }
        .chip b { display: block; font-size: 1rem; letter-spacing: -0.02em; }
        .chip span { color: var(--muted); font-size: 0.75rem; font-weight: 600; }

        .section-label {
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0.2rem 0 0.7rem;
        }
        .tile-art {
            border-radius: 16px;
            min-height: 92px;
            padding: 0.9rem 1rem;
            color: white !important;
            font-weight: 800;
            letter-spacing: -0.03em;
            display: flex;
            align-items: flex-end;
        }
        .tile-art.english { background: linear-gradient(135deg, #6d35e8, #a78bfa); }
        .tile-art.cnh { background: linear-gradient(135deg, #4c1d95, #7c3aed); }
        .tile-art span { color: white !important; font-size: 1.05rem; }
        .tile-copy { color: var(--muted); font-size: 0.88rem; line-height: 1.4; min-height: 2.6rem; margin: 0.55rem 0 0.2rem; }

        .rail h3 { margin: 0.15rem 0 0.15rem; font-size: 1.15rem; font-weight: 800; }
        .rail .hello { color: var(--muted) !important; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
        .rail-stat { display: flex; justify-content: space-between; padding: 0.55rem 0; border-bottom: 1px solid var(--line); font-size: 0.92rem; }
        .rail-stat b { font-weight: 800; }
        .bar-chart { display: flex; align-items: flex-end; gap: 0.45rem; height: 92px; margin: 0.85rem 0 0.15rem; }
        .bar-chart i {
            display: block; flex: 1; border-radius: 8px 8px 4px 4px;
            background: linear-gradient(180deg, #ddd6fe, #6d35e8);
            min-width: 0;
        }

        [data-testid="stMain"] [data-testid="stBaseButton-primary"] {
            background: var(--violet);
            border: none;
            border-radius: 999px;
            font-weight: 700;
            box-shadow: none;
        }
        [data-testid="stMain"] [data-testid="stBaseButton-secondary"] {
            border-radius: 999px;
            border-color: #e4def3;
            background: white;
            font-weight: 700;
        }

        [data-testid="stMain"] [data-testid="stRadio"] label {
            background: var(--paper);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.7rem 0.85rem;
            margin-bottom: 0.35rem;
        }
        [data-testid="stMain"] [data-testid="stRadio"] label:has(input:checked) {
            border-color: var(--violet);
            background: var(--violet-soft);
        }

        div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--paper);
            border-radius: 18px !important;
            border-color: var(--line) !important;
        }
        [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 16px; overflow: hidden; }

        .feedback-ok, .feedback-bad, .warn-box { border-radius: 14px; padding: 0.75rem 0.9rem; margin: 0.35rem 0 0.7rem; }
        .feedback-ok { background: #ecfdf5; }
        .feedback-bad { background: #fef2f2; }
        .warn-box { background: #fffbeb; }

        .hero-title { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; margin: 0; }
        .hero-subtitle, .section-desc, .empty-state { color: var(--muted); }
        .section-header { display: flex; gap: 0.75rem; align-items: center; margin: 1rem 0; }
        .section-icon {
            width: 42px; height: 42px; display: flex; align-items: center; justify-content: center;
            background: var(--violet-soft); border-radius: 12px; font-size: 1.3rem;
        }
        .section-title { font-weight: 750; margin: 0; }
        .card-panel, .empty-state, .revision-be-card {
            background: var(--paper); border: 1px solid var(--line); border-radius: 16px; padding: 1rem 1.1rem;
        }
        .empty-state { text-align: center; }
        .revision-formula {
            background: var(--violet-soft); border-radius: 12px; padding: 0.7rem 0.85rem;
            font-weight: 700; color: var(--violet-deep);
        }
        .tense-badge, .revision-wh-badge {
            display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px;
            background: var(--violet-soft); color: var(--violet); font-weight: 700; margin: 0 0.3rem 0.3rem 0;
        }
        .revision-contraction-row {
            display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid var(--line);
        }
        .revision-contraction-short { color: var(--violet); font-weight: 700; }
        .revision-be-form { font-size: 1.6rem; font-weight: 800; color: var(--violet); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge(course_id: str) -> str:
    if course_id == "cnh-al":
        return '<span class="course-badge badge-cnh">CNH — Alagoas</span>'
    return '<span class="course-badge badge-english">Inglês</span>'


def minutes(seconds: int) -> str:
    return f"{seconds // 3600} h {seconds % 3600 // 60} min" if seconds >= 3600 else f"{seconds // 60} min"


def page_title(title: str, lede: str = "") -> None:
    st.markdown(f'<h1 class="page-title">{title}</h1>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<p class="lede">{lede}</p>', unsafe_allow_html=True)


STATE_LABELS = {
    "nao_estudado": "Não estudado",
    "em_aprendizagem": "Em aprendizagem",
    "em_revisao": "Em revisão",
    "dominado": "Dominado",
}

from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path

import streamlit as st

CONFIG_PATH = Path(__file__).with_name("projects.json")
DEFAULT_CATEGORY = "Toutes"
PAGE_TITLE = "Automation SEO"


@dataclass(frozen=True)
class Project:
    name: str
    slug: str
    category: str
    status: str
    project_path: str
    entrypoint: str
    description: str
    evidence: tuple[str, ...]
    notes: str
    live_url: str = ""
    repository_url: str = ""
    documentation_url: str = ""


def load_catalog() -> list[Project]:
    try:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        st.error("Le fichier projects.json est introuvable.")
        st.stop()
    except json.JSONDecodeError as error:
        st.error(f"Le fichier projects.json est invalide : {error}")
        st.stop()

    return [
        Project(
            name=item["name"],
            slug=item["slug"],
            category=item["category"],
            status=item["status"],
            project_path=item["project_path"],
            entrypoint=item["entrypoint"],
            description=item["description"],
            evidence=tuple(item.get("evidence", [])),
            notes=item.get("notes", ""),
            live_url=item.get("live_url", ""),
            repository_url=item.get("repository_url", ""),
            documentation_url=item.get("documentation_url", ""),
        )
        for item in payload.get("validated_projects", [])
    ]


def get_category_marker(category: str) -> str:
    markers = {
        "Mots-cles": "KW",
        "GSC": "GSC",
        "SERP/IA": "AI",
        "Maillage interne": "LINK",
        "Scraping": "DATA",
        "Contenu": "TXT",
        "Technique": "TECH",
    }
    return markers.get(category, "SEO")


def matches_search(project: Project, query: str) -> bool:
    if not query:
        return True
    searchable_text = " ".join(
        [
            project.name,
            project.category,
            project.description,
        ]
    ).lower()
    return query.lower() in searchable_text


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --hub-background: #222429;
                --hub-deep: #0F1011;
                --hub-card: #27282A;
                --hub-card-strong: #1F2024;
                --hub-card-hover: #1B1C1E;
                --hub-border: #37383A;
                --hub-foreground: #F7F8F8;
                --hub-muted: #A1A1AA;
                --hub-muted-strong: #828282;
                --hub-accent: #49DCBC;
                --hub-good: #4CEBA6;
                --hub-risk: #FF3366;
                --hub-special: #B888EF;
                --hub-blue: #71A4F4;
                --hub-ring: rgba(73, 220, 188, 0.42);
                --hub-shadow: 0 20px 48px rgba(0, 0, 0, 0.28);
            }

            .stApp {
                background: var(--hub-background);
                color: var(--hub-foreground);
            }

            [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                background: transparent;
            }

            [data-testid="stSidebar"] {
                background: var(--hub-deep);
                border-right: 1px solid var(--hub-border);
            }

            [data-testid="stSidebar"] * {
                color: var(--hub-foreground);
            }

            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span {
                color: var(--hub-muted);
            }

            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {
                color: var(--hub-foreground);
            }

            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea,
            [data-testid="stSidebar"] [role="combobox"],
            [data-testid="stSidebar"] [data-baseweb="select"] > div,
            [data-testid="stSidebar"] [data-baseweb="input"] > div {
                background: var(--hub-card-strong);
                border: 1px solid var(--hub-border);
                border-radius: 8px;
                color: var(--hub-foreground) !important;
            }

            [data-testid="stSidebar"] [data-baseweb="select"] span,
            [data-testid="stSidebar"] [data-baseweb="select"] div,
            [data-testid="stSidebar"] [data-baseweb="input"] input,
            [data-testid="stSidebar"] [role="combobox"] {
                color: var(--hub-foreground) !important;
                -webkit-text-fill-color: var(--hub-foreground) !important;
            }

            [data-testid="stSidebar"] input::placeholder {
                color: var(--hub-muted-strong) !important;
                opacity: 1;
                -webkit-text-fill-color: var(--hub-muted-strong) !important;
            }

            [data-testid="stSidebar"] [data-baseweb="select"] svg {
                fill: var(--hub-muted) !important;
            }

            [data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div,
            [data-testid="stSidebar"] [data-baseweb="input"]:focus-within > div {
                border-color: var(--hub-accent);
                box-shadow: 0 0 0 2px var(--hub-ring);
            }

            [data-testid="stSidebar"] [role="radiogroup"] label {
                background: transparent !important;
                border: 0;
                color: var(--hub-muted) !important;
            }

            [data-testid="stSidebar"] [role="radiogroup"] label span {
                color: var(--hub-muted) !important;
            }

            [data-baseweb="popover"] [role="listbox"],
            [data-baseweb="menu"] {
                background: var(--hub-card-strong) !important;
                border: 1px solid var(--hub-border) !important;
                color: var(--hub-foreground) !important;
            }

            [data-baseweb="popover"] [role="option"],
            [data-baseweb="menu"] li {
                background: var(--hub-card-strong) !important;
                color: var(--hub-foreground) !important;
            }

            [data-baseweb="popover"] [role="option"]:hover,
            [data-baseweb="menu"] li:hover {
                background: var(--hub-card-hover) !important;
            }

            [data-baseweb="popover"] [role="option"][aria-selected="true"],
            [data-baseweb="popover"] [role="option"][aria-checked="true"],
            [role="option"][aria-selected="true"],
            [role="option"][aria-checked="true"] {
                background: rgba(73, 220, 188, 0.16) !important;
                color: var(--hub-foreground) !important;
            }

            .block-container {
                max-width: 1180px;
                padding-top: 1.6rem;
                padding-bottom: 4rem;
            }

            .hub-hero {
                border-bottom: 1px solid var(--hub-border);
                margin-bottom: 1.4rem;
                padding: 0.4rem 0 1.6rem;
            }

            .hub-kicker {
                color: var(--hub-accent);
                font-size: 0.76rem;
                font-weight: 800;
                letter-spacing: 0.12em;
                margin-bottom: 0.7rem;
                text-transform: uppercase;
            }

            .hub-title {
                color: var(--hub-foreground);
                font-size: 3.45rem;
                font-weight: 800;
                line-height: 1;
                margin: 0;
                max-width: 760px;
            }

            .hub-lead {
                color: var(--hub-muted);
                font-size: 1rem;
                line-height: 1.6;
                margin: 1rem 0 0;
                max-width: 760px;
            }

            .project-shell {
                background: var(--hub-card);
                border: 1px solid var(--hub-border);
                box-shadow: var(--hub-shadow);
            }

            .project-shell {
                border-radius: 8px;
                margin-bottom: 1rem;
                padding: 1.2rem;
                transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
            }

            .project-shell:hover {
                border-color: rgba(73, 220, 188, 0.52);
                box-shadow: 0 24px 56px rgba(0, 0, 0, 0.34);
                transform: translateY(-1px);
            }

            .project-head {
                align-items: start;
                display: grid;
                gap: 1rem;
                grid-template-columns: minmax(0, 1fr) minmax(160px, 0.24fr);
            }

            .category-token {
                align-items: center;
                aspect-ratio: 1;
                background: var(--hub-deep);
                border: 1px solid var(--hub-border);
                border-radius: 8px;
                color: var(--hub-accent);
                display: flex;
                flex: 0 0 auto;
                font-size: 0.72rem;
                font-weight: 900;
                height: 2.25rem;
                justify-content: center;
                width: 2.25rem;
            }

            .project-name {
                color: var(--hub-foreground);
                font-size: 1.35rem;
                font-weight: 700;
                line-height: 1.1;
                margin: 0;
            }

            .project-description {
                color: var(--hub-muted);
                line-height: 1.55;
                margin: 0.55rem 0 0;
            }

            .badge-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin-top: 0.8rem;
            }

            .badge {
                border: 1px solid var(--hub-border);
                border-radius: 999px;
                color: var(--hub-muted);
                display: inline-flex;
                font-size: 0.72rem;
                font-weight: 800;
                padding: 0.3rem 0.6rem;
                text-transform: uppercase;
            }

            .badge.validated {
                background: rgba(76, 235, 166, 0.15);
                border-color: rgba(76, 235, 166, 0.28);
                color: var(--hub-good);
            }

            .badge.cloud {
                background: rgba(73, 220, 188, 0.12);
                border-color: rgba(73, 220, 188, 0.25);
                color: var(--hub-accent);
            }

            .badge.backlog {
                background: rgba(255, 51, 102, 0.14);
                border-color: rgba(255, 51, 102, 0.28);
                color: var(--hub-risk);
            }

            .project-content {
                min-width: 0;
            }

            .project-title-row {
                align-items: center;
                display: flex;
                flex-wrap: wrap;
                gap: 0.7rem;
            }

            .app-link, .disabled-link {
                border-radius: 8px;
                display: flex;
                font-size: 0.88rem;
                font-weight: 800;
                justify-content: center;
                min-height: 2.55rem;
                padding: 0.72rem 0.9rem;
                text-align: center;
                text-decoration: none !important;
                transition: background-color 160ms ease, border-color 160ms ease, color 160ms ease, transform 160ms ease;
            }

            .app-link {
                background: var(--hub-foreground);
                border: 1px solid var(--hub-foreground);
                color: var(--hub-deep) !important;
                margin-bottom: 0.55rem;
            }

            .app-link:hover,
            .app-link:focus-visible {
                background: var(--hub-accent);
                border-color: var(--hub-accent);
                color: var(--hub-deep) !important;
                transform: translateY(-1px);
            }

            .app-link:focus-visible {
                outline: 2px solid var(--hub-ring);
                outline-offset: 2px;
            }

            .disabled-link {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.10);
                color: var(--hub-muted-strong);
            }

            .section-heading {
                align-items: end;
                display: flex;
                gap: 1rem;
                justify-content: space-between;
                margin: 2rem 0 1rem;
            }

            .section-heading h2 {
                color: var(--hub-foreground);
                font-size: 1.35rem;
                font-weight: 700;
                margin: 0;
            }

            .section-heading p {
                color: var(--hub-muted);
                margin: 0;
                max-width: 560px;
            }

            @media (max-width: 760px) {
                .project-head {
                    display: block;
                }

                .hub-title {
                    font-size: 2.35rem;
                }

                .category-token {
                    height: 2rem;
                    width: 2rem;
                }

                .section-heading {
                    align-items: start;
                    display: block;
                }

                .section-heading p {
                    margin-top: 0.5rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(available_count: int) -> None:
    st.markdown(
        f"""
        <section class="hub-hero">
            <div>
                <div class="hub-kicker">Automation SEO</div>
                <h1 class="hub-title">Lance tes outils SEO.</h1>
                <p class="hub-lead">
                    {available_count} outils disponibles. Filtre, choisis, ouvre le bon outil.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(projects: list[Project]) -> tuple[str, str, str]:
    categories = [DEFAULT_CATEGORY] + sorted({project.category for project in projects})

    with st.sidebar:
        st.markdown("## Explorer")
        selected_view = st.radio(
            "Vue",
            ["Disponibles", "Tous", "A venir"],
            horizontal=False,
        )
        selected_category = st.selectbox("Famille", categories)
        search_query = st.text_input("Recherche", placeholder="GSC, maillage, spin")

    return selected_category, search_query.strip(), selected_view


def filter_projects(
    projects: list[Project],
    selected_category: str,
    search_query: str,
    selected_view: str,
) -> list[Project]:
    filtered_projects = []
    for project in projects:
        if selected_category != DEFAULT_CATEGORY and project.category != selected_category:
            continue
        if not matches_search(project, search_query):
            continue
        if selected_view == "Disponibles" and not project.live_url:
            continue
        if selected_view == "A venir" and project.live_url:
            continue
        filtered_projects.append(project)
    return filtered_projects


def render_project(project: Project) -> None:
    marker = escape(get_category_marker(project.category))
    name = escape(project.name)
    category = escape(project.category)
    description = escape(project.description)
    live_badge = "Disponible" if project.live_url else "Bientot"
    live_badge_class = "badge validated" if project.live_url else "badge cloud"

    action_parts = [
        f'<a class="app-link" href="{escape(project.live_url)}" target="_blank" rel="noopener">Ouvrir</a>'
        if project.live_url
        else '<div class="disabled-link">Bientot disponible</div>'
    ]
    if project.documentation_url:
        action_parts.append(
            f'<a class="app-link" href="{escape(project.documentation_url)}" target="_blank" rel="noopener">Docs</a>'
        )
    actions_html = "".join(action_parts)
    project_html = "".join(
        [
            f'<article class="project-shell" id="{escape(project.slug)}">',
            '<div class="project-head">',
            '<div class="project-content">',
            '<div class="project-title-row">',
            f'<h2 class="project-name">{name}</h2>',
            f'<div class="category-token">{marker}</div>',
            "</div>",
            f'<p class="project-description">{description}</p>',
            '<div class="badge-row">',
            f'<span class="badge">{category}</span>',
            f'<span class="{live_badge_class}">{live_badge}</span>',
            "</div>",
            "</div>",
            f"<div>{actions_html}</div>",
            "</div>",
            "</article>",
        ]
    )

    st.markdown(project_html, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    inject_styles()

    projects = load_catalog()
    selected_category, search_query, selected_view = render_sidebar(projects)
    filtered_projects = filter_projects(projects, selected_category, search_query, selected_view)
    available_count = sum(1 for project in projects if project.live_url)

    render_hero(available_count)

    st.markdown(
        f"""
        <div class="section-heading">
            <div><h2>{escape(selected_view)}</h2></div>
            <p>Selectionne un outil, puis ouvre son interface dediee.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered_projects:
        for project in filtered_projects:
            render_project(project)
    else:
        st.info("Aucun outil ne correspond aux filtres actuels.")


if __name__ == "__main__":
    main()

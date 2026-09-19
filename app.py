from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_parser import extract_text, is_valid_resume_file
from text_cleaner import clean_text

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
JOB_ROLES_PATH = os.path.join(DATA_DIR, "job_roles.csv")
SKILL_DICT_PATH = os.path.join(DATA_DIR, "skill_dictionary.csv")


# ---------------------------------------------------------------------------
# Data loading (cached so it only runs once per session)
# ---------------------------------------------------------------------------

@st.cache_data
def load_job_roles() -> pd.DataFrame:
    df = pd.read_csv(JOB_ROLES_PATH)
    df["skills_list"] = df["required_skills"].apply(
        lambda s: [skill.strip().lower() for skill in s.split(",")]
    )
    return df


@st.cache_data
def load_skill_dictionary() -> pd.DataFrame:
    return pd.read_csv(SKILL_DICT_PATH)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def extract_skills(cleaned_text: str, skill_df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Find which dictionary skills appear in the cleaned resume text,
    grouped by category.
    """
    found: dict[str, list[str]] = {}
    for _, row in skill_df.iterrows():
        skill = str(row["skill"]).lower().strip()
        category = row["category"]
        # Word-boundary-ish check: skill appears as a substring surrounded
        # by non-alphanumeric chars or string edges.
        if f" {skill} " in f" {cleaned_text} ":
            found.setdefault(category, [])
            if skill not in found[category]:
                found[category].append(skill)
    return found


def flatten_skills(skills_by_category: dict[str, list[str]]) -> list[str]:
    flat = []
    for skills in skills_by_category.values():
        flat.extend(skills)
    return flat


def compute_match_scores(resume_text: str, job_roles_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a TF-IDF + cosine similarity match score between the resume
    text and each job role's required-skills text.
    """
    role_texts = job_roles_df["required_skills"].str.replace(",", " ").tolist()
    corpus = [resume_text] + role_texts

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    resume_vector = tfidf_matrix[0:1]
    role_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(resume_vector, role_vectors)[0]

    results = job_roles_df.copy()
    results["match_score"] = (similarities * 100).round(1)
    results = results.sort_values("match_score", ascending=False).reset_index(drop=True)
    return results


def build_roadmap(missing_skills: list[str]) -> list[str]:
    """Generate a simple week-by-week roadmap from missing skills."""
    roadmap = []
    for i, skill in enumerate(missing_skills[:6], start=1):
        roadmap.append(f"Week {i}: Learn the basics of {skill}")
    if not roadmap:
        roadmap.append("Great news — no major skill gaps found for this role!")
    return roadmap


def build_report_text(
    filename: str,
    target_role: str,
    match_score: float,
    found_skills: list[str],
    missing_skills: list[str],
    top_roles: pd.DataFrame,
    roadmap: list[str],
) -> str:
    found_lines = [f"- {s}" for s in found_skills] if found_skills else ["(none detected)"]
    missing_lines = (
        [f"- {s}" for s in missing_skills] if missing_skills else ["(none — good coverage!)"]
    )

    lines = [
        "AI RESUME ANALYZER - REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Resume file: {filename}",
        "",
        f"Target Role: {target_role}",
        f"Match Score: {match_score}%",
        "",
        "Skills Found:",
        *found_lines,
        "",
        "Missing Skills:",
        *missing_lines,
        "",
        "Recommended Roles:",
    ]
    for i, row in top_roles.head(3).iterrows():
        lines.append(f"{i + 1}. {row['role']} - {row['match_score']}%")

    lines.append("")
    lines.append("Suggested Roadmap:")
    lines.extend(roadmap)

    lines.append("")
    lines.append(
        "Note: This match score is an estimate to guide learning, not a "
        "hiring or rejection decision. Protected personal attributes are "
        "never used in scoring."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
    st.title("📄 AI Resume Analyzer & Job Recommendation System")
    st.caption(
        "Upload your resume to see how well it matches different job roles, "
        "what skills you're missing, and a simple roadmap to close the gap."
    )

    job_roles_df = load_job_roles()
    skill_df = load_skill_dictionary()

    # --- Sidebar: target role selection ---
    st.sidebar.header("Settings")
    target_role = st.sidebar.selectbox("Target job role", job_roles_df["role"].tolist())

    # --- Upload section ---
    st.header("1. Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

    if uploaded_file is None:
        st.info("Upload a resume to get started.")
        return

    st.write(f"**Uploaded file:** {uploaded_file.name}")

    is_valid, message = is_valid_resume_file(uploaded_file.name, uploaded_file.size)
    if not is_valid:
        st.error(message)
        return

    # --- Extraction & cleaning ---
    with st.spinner("Extracting and cleaning resume text..."):
        raw_text = extract_text(uploaded_file, filename=uploaded_file.name)
        cleaned = clean_text(raw_text)

    if not cleaned:
        st.error(
            "No readable text could be extracted. This may be a scanned/"
            "image-only resume — try a text-based PDF or DOCX instead."
        )
        return

    with st.expander("Show extracted & cleaned text"):
        st.text_area("Cleaned resume text", cleaned, height=200)

    # --- Skill extraction ---
    st.header("2. Extracted Skills")
    skills_by_category = extract_skills(cleaned, skill_df)
    all_found_skills = flatten_skills(skills_by_category)

    if skills_by_category:
        for category, skills in skills_by_category.items():
            st.markdown(f"**{category}:** {', '.join(skills)}")
    else:
        st.warning("No known skills were detected. Consider expanding the skill dictionary.")

    # --- Matching ---
    st.header("3. Match Score & Recommended Roles")
    results = compute_match_scores(cleaned, job_roles_df)

    st.bar_chart(results.set_index("role")["match_score"])

    top3 = results.head(3)
    cols = st.columns(3)
    for col, (_, row) in zip(cols, top3.iterrows()):
        col.metric(row["role"], f"{row['match_score']}%")

    # --- Skill gap for the selected target role ---
    st.header(f"4. Skill Gap for: {target_role}")
    target_row = job_roles_df[job_roles_df["role"] == target_role].iloc[0]
    required = set(target_row["skills_list"])
    found_set = set(all_found_skills)

    missing = sorted(required - found_set)
    matched = sorted(required & found_set)
    target_score = float(results.loc[results["role"] == target_role, "match_score"].iloc[0])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Skills you have")
        st.write(", ".join(matched) if matched else "None yet")
    with col2:
        st.subheader("❌ Skills to develop")
        st.write(", ".join(missing) if missing else "None — great coverage!")

    # --- Roadmap ---
    st.header("5. Suggested Learning Roadmap")
    roadmap = build_roadmap(missing)
    for step in roadmap:
        st.write(f"- {step}")

    # --- Downloadable report ---
    st.header("6. Download Report")
    report_text = build_report_text(
        filename=uploaded_file.name,
        target_role=target_role,
        match_score=target_score,
        found_skills=sorted(all_found_skills),
        missing_skills=missing,
        top_roles=results,
        roadmap=roadmap,
    )
    st.download_button(
        "Download analysis report (.txt)",
        data=report_text,
        file_name="resume_analysis_report.txt",
        mime="text/plain",
    )

    st.caption(
        "Match scores are estimates for guidance only. This tool does not "
        "use gender, age, religion, nationality, photo, marital status, or "
        "disability in scoring, and it is not a substitute for a recruiter's judgment."
    )


if __name__ == "__main__":
    main()

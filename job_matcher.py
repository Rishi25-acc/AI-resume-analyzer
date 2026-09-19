
from __future__ import annotations

import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
JOB_ROLES_PATH = os.path.join(DATA_DIR, "job_roles.csv")


def load_job_roles(path: str = JOB_ROLES_PATH) -> pd.DataFrame:
 
    df = pd.read_csv(path)
    df["skills_list"] = df["required_skills"].apply(
        lambda s: [skill.strip().lower() for skill in str(s).split(",") if skill.strip()]
    )
    return df


def compute_match_scores(resume_text: str, job_roles_df: pd.DataFrame) -> pd.DataFrame:
  
    if not resume_text:
        results = job_roles_df.copy()
        results["match_score"] = 0.0
        return results

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


def top_roles(results: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Return the top-N recommended roles by match score."""
    return results.sort_values("match_score", ascending=False).head(n).reset_index(drop=True)


def skill_gap(
    found_skills: list[str], job_roles_df: pd.DataFrame, target_role: str
) -> tuple[list[str], list[str]]:


    matches = job_roles_df[job_roles_df["role"] == target_role]
    if matches.empty:
        raise ValueError(f"Unknown target role: '{target_role}'")

    required = set(matches.iloc[0]["skills_list"])
    found_set = set(s.lower().strip() for s in found_skills)

    matched = sorted(required & found_set)
    missing = sorted(required - found_set)
    return matched, missing


# ---------------------------------------------------------------------------
# Manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    resume_sample = "python sql pandas machine learning scikit-learn docker numpy"

    roles_df = load_job_roles()
    ranked = compute_match_scores(resume_sample, roles_df)
    print("Ranked roles:")
    print(ranked[["role", "match_score"]])

    best_role = ranked.iloc[0]["role"]
    matched, missing = skill_gap(resume_sample.split(), roles_df, best_role)
    print(f"\nSkill gap for '{best_role}':")
    print("Matched:", matched)
    print("Missing:", missing)

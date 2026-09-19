"""
skill_extractor.py

Extracts known skills from cleaned resume text using a controlled skill
dictionary (data/skill_dictionary.csv), and groups them by category.

Usage:
    from skill_extractor import load_skill_dictionary, extract_skills, flatten_skills

    skill_df = load_skill_dictionary()
    skills_by_category = extract_skills(cleaned_text, skill_df)
    all_skills = flatten_skills(skills_by_category)
"""

from __future__ import annotations

import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SKILL_DICT_PATH = os.path.join(DATA_DIR, "skill_dictionary.csv")


def load_skill_dictionary(path: str = SKILL_DICT_PATH) -> pd.DataFrame:
    """
    Load the controlled skill dictionary from CSV.

    Expected columns: skill, category
    """
    df = pd.read_csv(path)
    df["skill"] = df["skill"].str.lower().str.strip()
    return df


def extract_skills(cleaned_text: str, skill_df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Search the cleaned resume text for every skill in the dictionary and
    group matches by category.

    A skill is considered "found" if it appears as a whole token/phrase
    surrounded by spaces (or the string edges), which avoids partial-word
    false positives (e.g. "java" inside "javascript").

    Args:
        cleaned_text: text already processed by text_cleaner.clean_text()
        skill_df: DataFrame with 'skill' and 'category' columns

    Returns:
        dict mapping category -> sorted list of matched skills
    """
    if not cleaned_text:
        return {}

    padded_text = f" {cleaned_text} "
    found: dict[str, list[str]] = {}

    # Sort skills by length (longest first) so multi-word skills like
    # "machine learning" are matched before shorter overlapping ones.
    sorted_df = skill_df.assign(_len=skill_df["skill"].str.len()).sort_values(
        "_len", ascending=False
    )

    for _, row in sorted_df.iterrows():
        skill = row["skill"]
        category = row["category"]
        padded_skill = f" {skill} "

        if padded_skill in padded_text:
            found.setdefault(category, [])
            if skill not in found[category]:
                found[category].append(skill)

    # Sort skills alphabetically within each category for stable output
    for category in found:
        found[category] = sorted(found[category])

    return found


def flatten_skills(skills_by_category: dict[str, list[str]]) -> list[str]:
    """Flatten a category->skills mapping into a single sorted list."""
    flat: list[str] = []
    for skills in skills_by_category.values():
        flat.extend(skills)
    return sorted(set(flat))


def skill_summary(skills_by_category: dict[str, list[str]]) -> str:
    """Produce a human-readable one-line-per-category summary string."""
    if not skills_by_category:
        return "No known skills detected."
    lines = []
    for category, skills in skills_by_category.items():
        lines.append(f"{category}: {', '.join(skills)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_text = (
        "skilled in python sql pandas machine learning tensorflow pytorch "
        "docker and git also familiar with power bi and nlp transformers"
    )

    skill_dict = load_skill_dictionary()
    result = extract_skills(sample_text, skill_dict)

    print("Skills by category:")
    print(skill_summary(result))
    print("\nFlattened:", flatten_skills(result))

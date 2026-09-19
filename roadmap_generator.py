from __future__ import annotations

from datetime import datetime

import pandas as pd

# A few skills get a slightly more specific study suggestion than the
# generic "Learn the basics of X" — extend this as the skill dictionary grows.


def build_roadmap(missing_skills: list[str], max_weeks: int = 6) -> list[str]:
    
    if not missing_skills:
        return ["Great news — no major skill gaps found for this role!"]

    roadmap = []
    for i, skill in enumerate(missing_skills[:max_weeks], start=1):
        tip = LEARNING_TIPS.get(skill.lower())
        if tip:
            roadmap.append(f"Week {i}: {skill.title()} — {tip}")
        else:
            roadmap.append(f"Week {i}: Learn the basics of {skill} through a short course or project.")

    if len(missing_skills) > max_weeks:
        remaining = len(missing_skills) - max_weeks
        roadmap.append(f"...and {remaining} more skill(s) to tackle after that.")

    return roadmap


def build_report_text(
    filename: str,
    target_role: str,
    match_score: float,
    found_skills: list[str],
    missing_skills: list[str],
    top_roles_df: pd.DataFrame,
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

    for i, row in top_roles_df.head(3).reset_index(drop=True).iterrows():
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
# Manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_missing = ["docker", "fastapi", "numpy"]
    for step in build_roadmap(demo_missing):
        print(step)

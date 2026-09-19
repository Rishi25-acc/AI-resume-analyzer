from __future__ import annotations

import re

PROTECTED_TOKENS = [
    "C++",
    "C#",
    ".NET",
    "ASP.NET",
    "Node.js",
    "React.js",
    "Vue.js",
    "Next.js",
    "D3.js",
    "TensorFlow.js",
    "Objective-C",
    "F#",
]


def _protect_tokens(text: str) -> tuple[str, dict[str, str]]:
    """Replace protected tokens with unique placeholders before cleaning."""
    placeholder_map: dict[str, str] = {}
    for i, token in enumerate(PROTECTED_TOKENS):
        if token.lower() in text.lower():
            placeholder = f"__PROTECTEDTOKEN{i}__"
            # Case-insensitive replace, but keep track of the canonical form
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            if pattern.search(text):
                text = pattern.sub(placeholder, text)
                placeholder_map[placeholder] = token.lower()
    return text, placeholder_map


def _restore_tokens(text: str, placeholder_map: dict[str, str]) -> str:
    """Swap placeholders back in for their protected token values."""
    for placeholder, original in placeholder_map.items():
        text = text.replace(placeholder.lower(), original)
    return text


def to_lowercase(text: str) -> str:
    """Lowercase all text for case-insensitive comparison."""
    return text.lower()


def remove_urls_and_emails(text: str) -> str:
    """Strip URLs and email addresses (not useful for skill matching)."""
    text = re.sub(r"http[s]?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    return text


def remove_special_characters(text: str) -> str:
    """
    Remove punctuation/symbols that aren't useful for matching, while
    keeping letters, numbers, +, #, ., and whitespace (needed for
    protected tokens like C++, C#, .NET after placeholder restoration,
    and for decimals/versions like "python 3.11").
    """
    text = re.sub(r"[^a-z0-9\s\+\#\.\_]", " ", text)
    return text


def normalize_whitespace(text: str) -> str:
    """Collapse repeated spaces/tabs/newlines into a single space and trim."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_isolated_periods(text: str) -> str:
  
    # Remove a period that is not immediately followed by a letter/digit
    # (i.e. not part of something like "3.11" or a still-protected token).
    text = re.sub(r"\.(?!\w)", " ", text)
    return text


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def clean_text(raw_text: str) -> str:

   
    if not raw_text or not raw_text.strip():
        return ""

    text, placeholder_map = _protect_tokens(raw_text)
    text = to_lowercase(text)
    text = remove_urls_and_emails(text)
    text = remove_special_characters(text)
    text = remove_isolated_periods(text)
    text = normalize_whitespace(text)
    text = _restore_tokens(text, placeholder_map)

    return text


# ---------------------------------------------------------------------------
# Manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = """
    John Doe
    Email: john.doe@example.com | Portfolio: https://johndoe.dev

    SKILLS: Python, C++, C#, .NET, SQL, ASP.NET, Machine Learning!!

    EXPERIENCE
    - Built REST APIs using   ASP.NET   and deployed on Azure.
    - Version: Python 3.11, used Node.js for the frontend.
    """

    print("--- RAW ---")
    print(sample)
    print("\n--- CLEANED ---")
    print(clean_text(sample))

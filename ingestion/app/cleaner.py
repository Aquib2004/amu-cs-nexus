# Text cleaning: remove noise and normalise whitespace.
#
# Parsed text often contains navigation, repeated blank lines, and stray
# spaces. Cleaning makes the text tidy and allows stable chunking later.

import re

_MULTISPACE = re.compile(r"[ \t\r\f\v]+")
_EXCESS_NEWLINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Collapse runs of spaces and excess blank lines, then strip edges."""
    text = _MULTISPACE.sub(" ", text)
    text = _EXCESS_NEWLINES.sub("\n\n", text)
    return text.strip()

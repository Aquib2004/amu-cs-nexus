# Text cleaning: remove noise and normalise whitespace.
#
# Parsed text often contains navigation, repeated blank lines, and stray
# spaces. Cleaning makes the text tidy and allows stable chunking later.

import html
import re

_MULTISPACE = re.compile(r"[ \t\r\f\v]+")
_EXCESS_NEWLINES = re.compile(r"\n{3,}")
# Zero-width / invisible characters that survive copy-paste and HTML parsing:
# U+FEFF (BOM), U+200B..U+200D (ZWSP/ZWNJ/ZWJ), U+2060 (word joiner),
# U+00AD (soft hyphen). Storing these corrupts chunk text and search matching.
_INVISIBLE = re.compile(r"[\ufeff\u200b-\u200d\u2060\u00ad]")
# Layout-only spaces rendered as non-breaking characters in HTML.
_LAYOUT_SPACES = re.compile(r"[\u00a0\u2007\u202f]")


def clean_text(text: str) -> str:
    """Normalise scraped text: decode entities, drop invisibles, tidy spacing.

    Decoding entities first matters: `&nbsp;` becomes a non-breaking space,
    which is then converted to a plain space by _LAYOUT_SPACES.
    """
    text = html.unescape(text)
    text = _INVISIBLE.sub("", text)
    text = _LAYOUT_SPACES.sub(" ", text)
    text = _MULTISPACE.sub(" ", text)
    text = _EXCESS_NEWLINES.sub("\n\n", text)
    return text.strip()
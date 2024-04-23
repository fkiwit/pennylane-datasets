import keyword
from typing import Annotated

import bibtexparser
from pydantic import AfterValidator, Field


def _python_identifier_validator(val: str) -> str:
    """Validator for ``PythonIdentifier``. Raises a ``ValueError`` if
    ``val.isidentifier()`` returns false or ``val`` is a
    keyword ('if', 'returns', etc)."""

    if not val.isidentifier() or val in keyword.kwlist:
        raise ValueError(f"Not a valid Python identifier: {repr(val)}")

    return val


"""
Field type for a legal Python identifier (name for a variable, class etc.)
"""
PythonIdentifier = Annotated[str, AfterValidator(_python_identifier_validator)]


def _bibtex_str_validator(val: str) -> str:
    """Validator for ``BibtexStr``. The BibTex parser is very permissive,
    and will parse almost any string as an "implicit comment block". This validator
    checks that at least one 'entry' (@article, @misc) is defined.
    """
    parsed = bibtexparser.parse_string(val)

    if parsed.failed_blocks:
        raise ValueError(
            f"Failed to parse Bibtex citation blocks: {repr(parsed.failed_blocks)}"
        )
    if not parsed.entries:
        raise ValueError("Bibtex citation has no entries")

    return val


"""Field type for a Bibtex citation string. Requires a valid Bibtex string
with at least one entry."""
BibtexStr = Annotated[str, AfterValidator(_bibtex_str_validator)]


"""Field type for a 'slug'. Must be 'kabob-case', and contain only
lowercase ASCII letters and numbers."""
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]

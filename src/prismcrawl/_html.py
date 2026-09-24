"""Decoding for ``html=True`` responses."""

from __future__ import annotations

import base64
from typing import Any, Mapping, Union

__all__ = ["decode_html"]


def decode_html(response: Union[Mapping[str, Any], str, bytes]) -> str:
    """Decode the source HTML from a response made with ``html=True``.

    Accepts the whole response, its ``data`` object, or the ``content`` string.
    The content is Base64-encoded, Brotli-compressed HTML; this needs the optional
    ``brotli`` dependency (``pip install "prismcrawl[html]"``).
    """
    content: Any = response
    if isinstance(content, Mapping) and "data" in content:
        content = content["data"]
    if isinstance(content, Mapping):
        if content.get("format") != "html+br+base64":
            raise ValueError("response does not contain HTML; make the request with html=True")
        content = content["content"]
    if not isinstance(content, (str, bytes)):
        raise TypeError("expected a response dict, its data object, or a Base64 string")

    try:
        import brotli
    except ImportError as error:
        raise ImportError('decode_html needs the brotli package: pip install "prismcrawl[html]"') from error
    raw: bytes = brotli.decompress(base64.b64decode(content))
    return raw.decode("utf-8", errors="replace")

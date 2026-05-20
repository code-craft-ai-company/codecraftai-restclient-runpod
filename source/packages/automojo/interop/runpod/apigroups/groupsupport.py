"""
    .. module:: groupsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains shared helpers used by the RunPod
                   api-group classes — URL composition and HTTP-error
                   reclassification.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import Any, Callable, Dict, Iterator, List, Optional
from urllib.parse import quote

from requests import Response

from automojo.errors.exceptions import SemanticError

from automojo.interop.runpod.exceptions.runpoderrors import (
    RunpodAuthenticationError, RunpodError
)


def encode_segment(*, segment: str) -> str:
    """
        Percent-encode a single URL path segment.

        :param segment: The path segment to encode. Must be a non-empty
            string.

        :returns: The percent-encoded segment.

        :raises: :class:`SemanticError` when ``segment`` is ``None`` or
            empty.
    """
    if segment is None:
        raise SemanticError("A RunPod URL path segment must not be None.")
    if not isinstance(segment, str):
        raise SemanticError("A RunPod URL path segment must be a string.")
    if len(segment) == 0:
        raise SemanticError("A RunPod URL path segment must not be empty.")

    rtnval = quote(segment, safe="")
    return rtnval


def compose_leaf(*, base: str, parts: List[str]) -> str:
    """
        Compose a REST leaf path by joining ``base`` with per-segment
        percent-encoded ``parts``.

        :param base: The base leaf path (e.g. ``"/v1"``).
        :param parts: The path segments to append. Each segment is
            percent-encoded; empty / ``None`` segments are rejected.

        :returns: The composed leaf path.

        :raises: :class:`SemanticError` when ``parts`` is ``None`` or holds
            an empty / ``None`` segment.
    """
    if parts is None:
        raise SemanticError("compose_leaf requires a non-None parts list.")

    encoded_parts: List[str] = []
    for part in parts:
        encoded_parts.append(encode_segment(segment=part))

    trimmed_base = base
    if trimmed_base.endswith("/"):
        trimmed_base = trimmed_base[:-1]

    joined = "/".join(encoded_parts)
    rtnval = "{}/{}".format(trimmed_base, joined)
    return rtnval


def raise_for_status(*, response: Response, action: str) -> None:
    """
        Reclassify a non-2xx RunPod response into a typed exception.

        :param response: The :class:`Response` to inspect.
        :param action: A short description of the attempted action.

        :returns: ``None``.

        :raises: :class:`RunpodAuthenticationError` on HTTP 401 / 403;
            :class:`RunpodError` on every other non-2xx status.
    """
    status = response.status_code
    if 200 <= status < 300:
        return

    err_msg_lines = ["RunPod API call failed: {}.".format(action)]
    err_msg_lines.append("STATUS: {}".format(status))
    err_msg_lines.append("RESPONSE:")
    err_msg_lines.append(response.text)
    err_msg = os.linesep.join(err_msg_lines)

    if status == 401 or status == 403:
        raise RunpodAuthenticationError(err_msg)

    raise RunpodError(err_msg)


def safe_json(*, response: Response) -> Dict[str, Any]:
    """
        Parse a response body as a JSON object, degrading to an empty dict.

        :param response: The :class:`Response` to parse.

        :returns: The decoded object, or an empty dict.
    """
    try:
        payload = response.json()
    except ValueError:
        rtnval: Dict[str, Any] = {}
        return rtnval

    if not isinstance(payload, dict):
        rtnval = {}
        return rtnval

    rtnval = payload
    return rtnval


def iter_cursor_pages(*, fetch_page: Callable[[Optional[str]], Dict[str, Any]],
                       items_field: str = "items",
                       cursor_field: str = "next") -> Iterator[Dict[str, Any]]:
    """
        Iterate a cursor-paginated RunPod endpoint, yielding each raw item
        dictionary across every page.

        :param fetch_page: Callable accepting the current cursor token
            (``None`` on the first call) and returning a page dictionary.
        :param items_field: Name of the field holding the page item list.
        :param cursor_field: Name of the field holding the next-page cursor
            token (``None`` / absent indicates the final page).

        :returns: An iterator over the raw item dictionaries.
    """
    cursor: Optional[str] = None
    while True:
        page = fetch_page(cursor)

        items = page.get(items_field)
        if items is None:
            items = []
        for item in items:
            yield item

        cursor = page.get(cursor_field)
        if cursor is None:
            break
    return


__all__ = ["encode_segment", "compose_leaf", "raise_for_status", "safe_json",
           "iter_cursor_pages"]

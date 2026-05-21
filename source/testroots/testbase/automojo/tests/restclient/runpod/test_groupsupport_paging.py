"""
    .. module:: test_groupsupport_paging
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Regression tests for ``iter_cursor_pages`` cursor
                   termination — guards against the empty-string-cursor
                   infinite loop (audit RC-H1) and the cursor-cycle
                   infinite loop (audit RC-H3).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest

from typing import Any, Dict, List, Optional

from automojo.restclient.runpod.apigroups.groupsupport import iter_cursor_pages
from automojo.restclient.runpod.exceptions.runpoderrors import RunpodError


def test_iter_cursor_pages_terminates_on_empty_string_cursor():
    """
        An empty-string ``next`` cursor must terminate traversal rather
        than loop forever (audit RC-H1).
    """
    pages = [
        {"items": [{"id": "a"}], "next": ""},
    ]
    call_count = {"n": 0}

    def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
        index = call_count["n"]
        call_count["n"] = index + 1
        page = pages[index]
        return page

    collected: List[Dict[str, Any]] = list(iter_cursor_pages(fetch_page=fetch_page))

    assert len(collected) == 1
    assert call_count["n"] == 1
    return


def test_iter_cursor_pages_terminates_on_none_cursor():
    """
        A ``None`` next cursor terminates traversal.
    """
    pages = [
        {"items": [{"id": "a"}], "next": "p2"},
        {"items": [{"id": "b"}], "next": None},
    ]
    call_count = {"n": 0}

    def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
        index = call_count["n"]
        call_count["n"] = index + 1
        page = pages[index]
        return page

    collected: List[Dict[str, Any]] = list(iter_cursor_pages(fetch_page=fetch_page))

    assert len(collected) == 2
    return


def test_iter_cursor_pages_raises_on_cursor_cycle():
    """
        A repeated cursor token must raise :class:`RunpodError` rather
        than loop forever (audit RC-H3).
    """
    def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
        page = {"items": [{"id": "x"}], "next": "stuck"}
        return page

    with pytest.raises(RunpodError):
        list(iter_cursor_pages(fetch_page=fetch_page))
    return

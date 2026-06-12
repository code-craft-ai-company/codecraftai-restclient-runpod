"""
    .. module:: test_properties
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Property-based tests (hypothesis) for the RunPod client —
                   paging cursor traversal totality, URL composition
                   determinism + per-segment encoding + rejection, and
                   waiter terminal-state correctness.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import pytest
import requests_mock as rm_module

from hypothesis import given, settings
from hypothesis import strategies as st

from ccai.errors.exceptions import SemanticError

from ccai.restclient.runpod.aspectsrunpod import AspectsRunpod
from ccai.restclient.runpod.apigroups.groupsupport import (
    compose_leaf, encode_segment, iter_cursor_pages
)
from ccai.restclient.runpod.exceptions.runpoderrors import (
    RunpodPodFailedError
)

from ccai.tests.restclient.runpod.testsupport import BASE_URL, make_client


# ----------------------------------------------------------------------
# Paging cursor traversal totality
# ----------------------------------------------------------------------

@settings(max_examples=60, deadline=None)
@given(page_sizes=st.lists(st.integers(min_value=0, max_value=8),
                           min_size=1, max_size=6))
def test_paging_traversal_yields_every_item(page_sizes):
    """
        Cursor traversal visits every item across an arbitrary chain of
        pages exactly once and in order.
    """
    pages = []
    counter = 0
    for index, size in enumerate(page_sizes):
        items = []
        for _ in range(size):
            items.append({"id": counter})
            counter = counter + 1
        is_last = index == (len(page_sizes) - 1)
        cursor = None
        if is_last is False:
            cursor = "c{}".format(index)
        pages.append({"items": items, "next": cursor})

    page_iter = iter(pages)

    def fetch_page(cursor):
        return next(page_iter)

    collected = list(iter_cursor_pages(fetch_page=fetch_page))
    expected = list(range(counter))
    assert [entry["id"] for entry in collected] == expected


@settings(max_examples=40, deadline=None)
@given(total=st.integers(min_value=0, max_value=25))
def test_list_pods_paging_totality_over_http(total):
    """
        ``list_pods`` follows cursors transparently and returns every pod.
    """
    client = make_client()
    aspects = AspectsRunpod(page_size=10)

    pods = [{"id": "pod-{}".format(i), "desiredStatus": "RUNNING"}
            for i in range(total)]

    chunk = 7
    responses = []
    offset = 0
    while True:
        slice_items = pods[offset:offset + chunk]
        offset = offset + chunk
        cursor = None
        if offset < total:
            cursor = "c{}".format(offset)
        responses.append({"json": {"items": slice_items, "next": cursor}})
        if offset >= total:
            break

    with rm_module.Mocker() as mock:
        mock.get("{}/v1/pods".format(BASE_URL), responses)
        result = client.list_pods(aspects=aspects)

    assert len(result) == total


# ----------------------------------------------------------------------
# URL composition
# ----------------------------------------------------------------------

@settings(max_examples=80, deadline=None)
@given(segments=st.lists(st.text(min_size=1, max_size=12),
                         min_size=1, max_size=4))
def test_compose_leaf_is_deterministic(segments):
    """
        URL composition is deterministic for the same segment list.
    """
    first = compose_leaf(base="/v1", parts=list(segments))
    second = compose_leaf(base="/v1", parts=list(segments))
    assert first == second


@settings(max_examples=80, deadline=None)
@given(segment=st.text(min_size=1, max_size=20))
def test_encode_segment_is_per_segment_safe(segment):
    """
        Per-segment encoding never emits a raw path separator.
    """
    encoded = encode_segment(segment=segment)
    assert "/" not in encoded


def test_compose_leaf_rejects_empty_segment():
    """
        An empty path segment is rejected with SemanticError.
    """
    with pytest.raises(SemanticError):
        compose_leaf(base="/v1", parts=["pods", ""])


def test_compose_leaf_rejects_none_segment():
    """
        A ``None`` path segment is rejected with SemanticError.
    """
    with pytest.raises(SemanticError):
        compose_leaf(base="/v1", parts=["pods", None])


# ----------------------------------------------------------------------
# wait_until_running terminal-state correctness
# ----------------------------------------------------------------------

_NON_TERMINAL = ("PENDING", "CREATED", "PROVISIONING")


@settings(max_examples=40, deadline=None)
@given(prefix=st.lists(st.sampled_from(_NON_TERMINAL),
                       min_size=0, max_size=5),
       terminal=st.sampled_from(("RUNNING", "FAILED")))
def test_waiter_resolves_to_first_terminal_state(prefix, terminal):
    """
        Against a monotonic status stream the waiter resolves to the first
        terminal state — RUNNING returns, FAILED raises.
    """
    client = make_client()
    aspects = AspectsRunpod(pod_poll_interval_seconds=0.0,
                            pod_running_timeout_seconds=30.0)

    stream = []
    for status in prefix:
        stream.append({"json": {"id": "pod-1", "desiredStatus": status}})
    stream.append({"json": {"id": "pod-1", "desiredStatus": terminal}})

    with rm_module.Mocker() as mock:
        mock.get("{}/v1/pods/pod-1".format(BASE_URL), stream)
        if terminal == "RUNNING":
            pod = client.wait_until_running(pod_id="pod-1", aspects=aspects)
            assert pod.is_running is True
        else:
            with pytest.raises(RunpodPodFailedError):
                client.wait_until_running(pod_id="pod-1", aspects=aspects)

"""
    .. module:: test_construction
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Construction and authentication tests for RunpodClient.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase


import requests_mock as rm_module

from ccai.errors.exceptions import ConfigurationError

from ccai.credentials.basiccredential import BasicCredential

from ccai.restclient.runpod.runpodclient import RunpodClient
from ccai.restclient.runpod.exceptions.runpoderrors import (
    RunpodAuthenticationError
)

from .testsupport import (
    BASE_URL, make_client, make_credential
)


def test_construction_with_runpod_credential():
    """
        A client constructed with a :class:`RunpodApiKeyCredential` exposes
        every api group.
    """
    client = make_client()
    assert client.gpu_types is not None
    assert client.data_centers is not None
    assert client.pod_templates is not None
    assert client.network_volumes is not None
    assert client.pods is not None
    assert client.tags is not None


def test_construction_rejects_wrong_credential_type():
    """
        Constructing with a non-RunPod credential raises ConfigurationError.
    """
    wrong = BasicCredential(identifier="b", categories=["basic"],
                            username="u", password="p")
    with testbase.raises(ConfigurationError):
        RunpodClient(credential=wrong)


def test_bearer_token_attached_to_request():
    """
        Outbound calls carry the Bearer-token Authorization header.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), json=[])
        client.list_gpu_types()
        auth = mock.last_request.headers.get("Authorization")
        assert auth == "Bearer rpa_test_0001"


def test_http_401_reclassifies_to_authentication_error():
    """
        An HTTP 401 reclassifies into RunpodAuthenticationError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), status_code=401,
                 text="unauthorized")
        with testbase.raises(RunpodAuthenticationError):
            client.list_gpu_types()


def test_http_403_reclassifies_to_authentication_error():
    """
        An HTTP 403 reclassifies into RunpodAuthenticationError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), status_code=403,
                 text="forbidden")
        with testbase.raises(RunpodAuthenticationError):
            client.list_gpu_types()

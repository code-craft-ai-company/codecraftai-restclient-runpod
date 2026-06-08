"""
    .. module:: testsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Shared construction helpers for the RunPod REST client
                   test suite.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai.credentials.runpodapikeycredential import RunpodApiKeyCredential

from ccai.restclient.runpod.runpodclient import RunpodClient


TEST_HOST = "rest.runpod.test"

BASE_URL = "https://{}".format(TEST_HOST)


def make_credential() -> RunpodApiKeyCredential:
    """
        Build a :class:`RunpodApiKeyCredential` for tests.

        :returns: A populated RunPod API-key credential.
    """
    rtnval = RunpodApiKeyCredential(identifier="runpod-test-key",
                                    categories=["hpc-venue"],
                                    token="rpa_test_0001")
    return rtnval


def make_client() -> RunpodClient:
    """
        Build a :class:`RunpodClient` bound to the test host.

        :returns: A constructed RunPod REST client.
    """
    rtnval = RunpodClient(credential=make_credential(), host=TEST_HOST)
    return rtnval

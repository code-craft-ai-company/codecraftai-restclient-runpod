"""
    .. module:: test_apigroups
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Example-based tests for the RunPod api groups — idempotent
                   template / volume create, pod launch + terminate, secure
                   vs community selection, tagging, and waiter behaviour.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase


import requests_mock as rm_module

from ccai.errors.exceptions import SemanticError

from ccai.restclient.runpod.aspectsrunpod import AspectsRunpod
from ccai.restclient.runpod.enums.runpodcloudtype import RunpodCloudType
from ccai.restclient.runpod.exceptions.runpoderrors import (
    RunpodAcceleratorNotAvailableError, RunpodCapacityUnavailableError,
    RunpodPodFailedError
)
from ccai.restclient.runpod.specs.runpodpodlaunchspec import (
    RunpodPodLaunchSpec
)
from ccai.restclient.runpod.specs.runpodnetworkvolumespec import (
    RunpodNetworkVolumeSpec
)
from ccai.restclient.runpod.specs.runpodpodtemplatespec import (
    RunpodPodTemplateSpec
)

from .testsupport import BASE_URL, make_client


_GPU_CATALOG = [
    {"id": "NVIDIA A100", "displayName": "A100", "memoryInGb": 80,
     "secureDataCenters": ["US-CA-1"], "communityDataCenters": ["EU-1"]},
    {"id": "NVIDIA L4", "displayName": "L4", "memoryInGb": 24,
     "secureDataCenters": [], "communityDataCenters": ["EU-1"]},
]


def test_list_gpu_types_parses_records():
    """
        ``list_gpu_types`` parses every catalog entry.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), json=_GPU_CATALOG)
        gpu_types = client.list_gpu_types()
    assert len(gpu_types) == 2
    assert gpu_types[0].gpu_type_id == "NVIDIA A100"
    assert gpu_types[0].memory_gb == 80


def test_list_data_centers_parses_records():
    """
        ``list_data_centers`` parses every catalog entry.
    """
    client = make_client()
    body = [{"id": "US-CA-1", "name": "California", "secureCloud": True}]
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/datacenters".format(BASE_URL), json=body)
        data_centers = client.list_data_centers()
    assert len(data_centers) == 1
    assert data_centers[0].secure_cloud is True


def test_create_pod_template_idempotent_on_name():
    """
        Creating a template whose name already exists returns the existing
        template and issues no POST.
    """
    client = make_client()
    existing = {"items": [{"id": "t-1", "name": "trainer",
                           "imageName": "img:1"}]}
    spec = RunpodPodTemplateSpec(name="trainer", image_name="img:1")
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/templates".format(BASE_URL), json=existing)
        post = mock.post("{}/v1/templates".format(BASE_URL), json={})
        template = client.create_pod_template(spec=spec)
        assert post.call_count == 0
    assert template.template_id == "t-1"


def test_create_pod_template_posts_when_absent():
    """
        Creating a new template issues a POST and returns the created
        record.
    """
    client = make_client()
    spec = RunpodPodTemplateSpec(name="fresh", image_name="img:2")
    created = {"id": "t-9", "name": "fresh", "imageName": "img:2"}
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/templates".format(BASE_URL), json={"items": []})
        post = mock.post("{}/v1/templates".format(BASE_URL), json=created)
        template = client.create_pod_template(spec=spec)
        assert post.call_count == 1
    assert template.template_id == "t-9"


def test_delete_pod_template_unknown_id_is_noop():
    """
        Deleting an unknown template id succeeds as a no-op.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.delete("{}/v1/templates/t-x".format(BASE_URL), status_code=404)
        client.delete_pod_template(template_id="t-x")


def test_create_network_volume_idempotent_on_name_and_dc():
    """
        Creating a volume whose name + data center already exist returns the
        existing volume and issues no POST.
    """
    client = make_client()
    existing = {"items": [{"id": "v-1", "name": "data", "size": 100,
                           "dataCenterId": "US-CA-1"}]}
    spec = RunpodNetworkVolumeSpec(name="data", size_gb=100,
                                   data_center_id="US-CA-1")
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/networkvolumes".format(BASE_URL), json=existing)
        post = mock.post("{}/v1/networkvolumes".format(BASE_URL), json={})
        volume = client.create_network_volume(spec=spec)
        assert post.call_count == 0
    assert volume.volume_id == "v-1"


def test_launch_pod_secure_happy_path():
    """
        A Secure Cloud launch against an available GPU type POSTs the pod.
    """
    client = make_client()
    spec = RunpodPodLaunchSpec(name="p1", gpu_type_id="NVIDIA A100",
                               template_id="t-1",
                               cloud_type=RunpodCloudType.SECURE)
    created = {"id": "pod-1", "name": "p1", "desiredStatus": "PENDING"}
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), json=_GPU_CATALOG)
        mock.post("{}/v1/pods".format(BASE_URL), json=created)
        pod = client.launch_pod(spec=spec)
    assert pod.pod_id == "pod-1"


def test_launch_pod_unavailable_gpu_raises():
    """
        Launching against a GPU type absent from the catalog raises
        RunpodAcceleratorNotAvailableError.
    """
    client = make_client()
    spec = RunpodPodLaunchSpec(name="p1", gpu_type_id="NVIDIA H999",
                               template_id="t-1")
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), json=_GPU_CATALOG)
        with testbase.raises(RunpodAcceleratorNotAvailableError):
            client.launch_pod(spec=spec)


def test_launch_pod_secure_capacity_unavailable_raises():
    """
        A Secure Cloud launch against a GPU type with no Secure capacity
        raises RunpodCapacityUnavailableError.
    """
    client = make_client()
    spec = RunpodPodLaunchSpec(name="p1", gpu_type_id="NVIDIA L4",
                               template_id="t-1",
                               cloud_type=RunpodCloudType.SECURE)
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), json=_GPU_CATALOG)
        with testbase.raises(RunpodCapacityUnavailableError):
            client.launch_pod(spec=spec)


def test_launch_pod_community_succeeds_for_community_only_gpu():
    """
        A Community Cloud launch against a community-only GPU type POSTs the
        pod.
    """
    client = make_client()
    spec = RunpodPodLaunchSpec(name="p1", gpu_type_id="NVIDIA L4",
                               template_id="t-1",
                               cloud_type=RunpodCloudType.COMMUNITY)
    created = {"id": "pod-2", "name": "p1", "desiredStatus": "PENDING"}
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/gpuTypes".format(BASE_URL), json=_GPU_CATALOG)
        mock.post("{}/v1/pods".format(BASE_URL), json=created)
        pod = client.launch_pod(spec=spec)
    assert pod.pod_id == "pod-2"


def test_launch_spec_rejects_bad_cloud_type():
    """
        An unrecognised cloud_type raises SemanticError at spec construction.
    """
    with testbase.raises(SemanticError):
        RunpodPodLaunchSpec(name="p", gpu_type_id="g", cloud_type="HYBRID")


def test_terminate_pod_already_terminated_is_noop():
    """
        Terminating an already-terminated pod succeeds as a no-op.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.delete("{}/v1/pods/pod-x".format(BASE_URL), status_code=404)
        client.terminate_pod(pod_id="pod-x")


def test_start_and_stop_pod_return_updated_record():
    """
        ``start_pod`` / ``stop_pod`` POST the lifecycle verb and parse the
        updated pod.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.post("{}/v1/pods/pod-1/start".format(BASE_URL),
                  json={"id": "pod-1", "desiredStatus": "RUNNING"})
        mock.post("{}/v1/pods/pod-1/stop".format(BASE_URL),
                  json={"id": "pod-1", "desiredStatus": "EXITED"})
        started = client.start_pod(pod_id="pod-1")
        stopped = client.stop_pod(pod_id="pod-1")
    assert started.desired_status == "RUNNING"
    assert stopped.desired_status == "EXITED"


def test_apply_tags_patches_resource():
    """
        ``apply_tags`` PATCHes the resource with the supplied tag set.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        patch = mock.patch("{}/v1/pods/pod-1".format(BASE_URL), json={})
        client.apply_tags(resource_type="pods", resource_id="pod-1",
                          tags={"run": "r1"})
        assert patch.call_count == 1


def test_apply_tags_rejects_bad_resource_type():
    """
        ``apply_tags`` with an unsupported resource type raises
        SemanticError.
    """
    client = make_client()
    with testbase.raises(SemanticError):
        client.apply_tags(resource_type="widgets", resource_id="x",
                          tags={})


def test_wait_until_running_returns_when_running():
    """
        ``wait_until_running`` returns the pod once it is RUNNING.
    """
    client = make_client()
    aspects = AspectsRunpod(pod_poll_interval_seconds=0.0,
                            pod_running_timeout_seconds=5.0)
    responses = [{"json": {"id": "pod-1", "desiredStatus": "PENDING"}},
                 {"json": {"id": "pod-1", "desiredStatus": "RUNNING"}}]
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/pods/pod-1".format(BASE_URL), responses)
        pod = client.wait_until_running(pod_id="pod-1", aspects=aspects)
    assert pod.is_running is True


def test_wait_until_running_raises_on_failed_state():
    """
        ``wait_until_running`` raises RunpodPodFailedError on a terminal
        failed state.
    """
    client = make_client()
    aspects = AspectsRunpod(pod_poll_interval_seconds=0.0)
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/pods/pod-1".format(BASE_URL),
                 json={"id": "pod-1", "desiredStatus": "FAILED"})
        with testbase.raises(RunpodPodFailedError):
            client.wait_until_running(pod_id="pod-1", aspects=aspects)


def test_wait_until_running_times_out():
    """
        ``wait_until_running`` raises TimeoutError when the budget elapses.
    """
    client = make_client()
    aspects = AspectsRunpod(pod_poll_interval_seconds=0.0,
                            pod_running_timeout_seconds=0.0)
    with rm_module.Mocker() as mock:
        mock.get("{}/v1/pods/pod-1".format(BASE_URL),
                 json={"id": "pod-1", "desiredStatus": "PENDING"})
        with testbase.raises(TimeoutError):
            client.wait_until_running(pod_id="pod-1", aspects=aspects)

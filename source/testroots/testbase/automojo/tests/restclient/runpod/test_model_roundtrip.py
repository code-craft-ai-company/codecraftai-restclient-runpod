"""
    .. module:: test_model_roundtrip
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Round-trip tests verifying that every hand-authored RunPod
                   model record is reconstructed exactly by
                   ``from_dict(to_dict(x))``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai.restclient.runpod.model.runpoddatacenter import (
    RunpodDataCenter
)
from ccai.restclient.runpod.model.runpodgputype import RunpodGpuType
from ccai.restclient.runpod.model.runpodnetworkvolume import (
    RunpodNetworkVolume
)
from ccai.restclient.runpod.model.runpodpod import RunpodPod, RunpodPort
from ccai.restclient.runpod.model.runpodpodtemplate import (
    RunpodPodTemplate
)


def test_data_center_roundtrip() -> None:
    """
        A populated :class:`RunpodDataCenter` survives the round trip.
    """
    original = RunpodDataCenter(data_center_id="US-CA-1", name="California",
                                secure_cloud=True)
    rebuilt = RunpodDataCenter.from_dict(original.to_dict())

    assert rebuilt.data_center_id == original.data_center_id
    assert rebuilt.name == original.name
    assert rebuilt.secure_cloud == original.secure_cloud
    return


def test_gpu_type_roundtrip() -> None:
    """
        A populated :class:`RunpodGpuType` survives the round trip.
    """
    original = RunpodGpuType(gpu_type_id="NVIDIA H100 80GB",
                             display_name="H100", memory_gb=80,
                             secure_data_centers=["US-CA-1"],
                             community_data_centers=["US-TX-1", "EU-SE-1"])
    rebuilt = RunpodGpuType.from_dict(original.to_dict())

    assert rebuilt.gpu_type_id == original.gpu_type_id
    assert rebuilt.display_name == original.display_name
    assert rebuilt.memory_gb == original.memory_gb
    assert rebuilt.secure_data_centers == original.secure_data_centers
    assert rebuilt.community_data_centers == original.community_data_centers
    return


def test_network_volume_roundtrip() -> None:
    """
        A populated :class:`RunpodNetworkVolume` survives the round trip.
    """
    original = RunpodNetworkVolume(volume_id="vol-1", name="data",
                                   size_gb=200, data_center_id="US-CA-1")
    rebuilt = RunpodNetworkVolume.from_dict(original.to_dict())

    assert rebuilt.volume_id == original.volume_id
    assert rebuilt.name == original.name
    assert rebuilt.size_gb == original.size_gb
    assert rebuilt.data_center_id == original.data_center_id
    return


def test_port_roundtrip() -> None:
    """
        A populated :class:`RunpodPort` survives the round trip.
    """
    original = RunpodPort(private_port=8888, public_port=40001,
                          ip="1.2.3.4", protocol="http")
    rebuilt = RunpodPort.from_dict(original.to_dict())

    assert rebuilt.private_port == original.private_port
    assert rebuilt.public_port == original.public_port
    assert rebuilt.ip == original.ip
    assert rebuilt.protocol == original.protocol
    return


def test_pod_roundtrip() -> None:
    """
        A populated :class:`RunpodPod` survives the round trip, including
        its nested port mappings.
    """
    port = RunpodPort(private_port=22, public_port=40000,
                      ip="1.2.3.4", protocol="tcp")
    original = RunpodPod(pod_id="pod-1", name="trainer",
                         desired_status="RUNNING",
                         gpu_type_id="NVIDIA H100 80GB", gpu_count=8,
                         image_name="runpod/pytorch:latest",
                         public_ip="1.2.3.4", ports=[port],
                         ssh_endpoint="ssh://pod-1@1.2.3.4:40000")
    rebuilt = RunpodPod.from_dict(original.to_dict())

    assert rebuilt.pod_id == original.pod_id
    assert rebuilt.name == original.name
    assert rebuilt.desired_status == original.desired_status
    assert rebuilt.gpu_type_id == original.gpu_type_id
    assert rebuilt.gpu_count == original.gpu_count
    assert rebuilt.image_name == original.image_name
    assert rebuilt.public_ip == original.public_ip
    assert rebuilt.ssh_endpoint == original.ssh_endpoint
    assert len(rebuilt.ports) == 1
    assert rebuilt.ports[0].private_port == port.private_port
    assert rebuilt.ports[0].public_port == port.public_port
    assert rebuilt.ports[0].ip == port.ip
    assert rebuilt.ports[0].protocol == port.protocol
    return


def test_pod_template_roundtrip() -> None:
    """
        A populated :class:`RunpodPodTemplate` survives the round trip.
    """
    original = RunpodPodTemplate(template_id="tpl-1", name="pytorch",
                                 image_name="runpod/pytorch:latest",
                                 container_disk_gb=40,
                                 container_start_command="bash start.sh")
    rebuilt = RunpodPodTemplate.from_dict(original.to_dict())

    assert rebuilt.template_id == original.template_id
    assert rebuilt.name == original.name
    assert rebuilt.image_name == original.image_name
    assert rebuilt.container_disk_gb == original.container_disk_gb
    assert (rebuilt.container_start_command ==
            original.container_start_command)
    return

"""
    .. module:: runpodpodlaunchspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodPodLaunchSpec`
                   describing a pod launch request.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Union

from ccai.errors.exceptions import SemanticError

from ccai.restclient.runpod.enums.runpodcloudtype import RunpodCloudType


class RunpodPodLaunchSpec:
    """
        A pod launch request.

        Carries the GPU type and count, the pod template, the pod name, the
        container disk size, the network-volume mount list, the exposed
        ports, the environment-variable map, the capacity-tier cloud type,
        and an optional container start command override.
    """

    def __init__(self, *, name: str, gpu_type_id: str, gpu_count: int = 1,
                 template_id: Optional[str] = None,
                 image_name: Optional[str] = None,
                 container_disk_gb: int = 10,
                 volume_mounts: Optional[List[str]] = None,
                 ports: Optional[List[str]] = None,
                 env: Optional[Dict[str, str]] = None,
                 cloud_type: Union[RunpodCloudType, str] = RunpodCloudType.SECURE,
                 container_start_command: Optional[str] = None) -> None:
        """
            Initialize a :class:`RunpodPodLaunchSpec`.

            :param name: The pod name.
            :param gpu_type_id: The RunPod GPU type identifier.
            :param gpu_count: The number of GPUs to attach.
            :param template_id: The pod template identifier.
            :param image_name: An inline container image (when no template).
            :param container_disk_gb: Container disk size in GiB.
            :param volume_mounts: Network-volume identifiers to attach.
            :param ports: Port mapping strings (e.g. ``"8888/http"``).
            :param env: Environment-variable map.
            :param cloud_type: The capacity-tier cloud type.
            :param container_start_command: Optional container start command
                override (used to render userspace Tailscale bring-up).

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``cloud_type`` is not a
                recognized value.
        """
        if isinstance(cloud_type, RunpodCloudType):
            cloud_type_value = cloud_type
        elif isinstance(cloud_type, str):
            try:
                cloud_type_value = RunpodCloudType(cloud_type)
            except ValueError:
                err_msg = ("RunpodPodLaunchSpec.cloud_type must be SECURE or "
                           "COMMUNITY, got {!r}.".format(cloud_type))
                raise SemanticError(err_msg) from None
        else:
            err_msg = ("RunpodPodLaunchSpec.cloud_type must be a "
                       "RunpodCloudType or string.")
            raise SemanticError(err_msg)

        self.name = name
        self.gpu_type_id = gpu_type_id
        self.gpu_count = gpu_count
        self.template_id = template_id
        self.image_name = image_name
        self.container_disk_gb = container_disk_gb
        self.volume_mounts: List[str] = []
        if volume_mounts is not None:
            self.volume_mounts = list(volume_mounts)
        self.ports: List[str] = []
        if ports is not None:
            self.ports = list(ports)
        self.env: Dict[str, str] = {}
        if env is not None:
            self.env = dict(env)
        self.cloud_type = cloud_type_value
        self.container_start_command = container_start_command
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Render the spec into a RunPod API request body.

            :returns: A request-body dictionary.
        """
        payload: Dict[str, Any] = {
            "name": self.name,
            "gpuTypeId": self.gpu_type_id,
            "gpuCount": self.gpu_count,
            "containerDiskInGb": self.container_disk_gb,
            "cloudType": self.cloud_type.value,
        }
        if self.template_id is not None:
            payload["templateId"] = self.template_id
        if self.image_name is not None:
            payload["imageName"] = self.image_name
        if len(self.volume_mounts) > 0:
            payload["networkVolumeIds"] = list(self.volume_mounts)
        if len(self.ports) > 0:
            payload["ports"] = list(self.ports)
        if len(self.env) > 0:
            payload["env"] = dict(self.env)
        if self.container_start_command is not None:
            payload["dockerArgs"] = self.container_start_command

        rtnval = payload
        return rtnval


__all__ = ["RunpodPodLaunchSpec"]

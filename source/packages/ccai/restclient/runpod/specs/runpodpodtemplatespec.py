"""
    .. module:: runpodpodtemplatespec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodPodTemplateSpec`
                   describing a pod-template create request.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional


class RunpodPodTemplateSpec:
    """
        A pod-template create request.

        Carries the template name, the container image reference, the
        container disk size in GiB, and an optional default container start
        command.
    """

    def __init__(self, *, name: str, image_name: str,
                 container_disk_gb: int = 10,
                 container_start_command: Optional[str] = None) -> None:
        """
            Initialize a :class:`RunpodPodTemplateSpec`.

            :param name: The template name.
            :param image_name: The container image reference.
            :param container_disk_gb: Container disk size in GiB.
            :param container_start_command: Optional default container start
                command.

            :returns: ``None``.
        """
        self.name = name
        self.image_name = image_name
        self.container_disk_gb = container_disk_gb
        self.container_start_command = container_start_command
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Render the spec into a RunPod API request body.

            :returns: A request-body dictionary.
        """
        payload: Dict[str, Any] = {
            "name": self.name,
            "imageName": self.image_name,
            "containerDiskInGb": self.container_disk_gb,
        }
        if self.container_start_command is not None:
            payload["dockerArgs"] = self.container_start_command

        rtnval = payload
        return rtnval


__all__ = ["RunpodPodTemplateSpec"]

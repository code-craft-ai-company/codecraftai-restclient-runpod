"""
    .. module:: runpodpodtemplate
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodPodTemplate` model
                   describing a RunPod pod template.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional


class RunpodPodTemplate:
    """
        A RunPod pod template.

        Carries the provider template identifier, the template name, the
        container image reference, the container disk size in GiB, and the
        optional default container start command.
    """

    def __init__(self, *, template_id: str, name: str, image_name: str,
                 container_disk_gb: int = 10,
                 container_start_command: Optional[str] = None) -> None:
        """
            Initialize a :class:`RunpodPodTemplate`.

            :param template_id: The RunPod template identifier.
            :param name: The template name.
            :param image_name: The container image reference.
            :param container_disk_gb: Container disk size in GiB.
            :param container_start_command: Optional default container start
                command.

            :returns: ``None``.
        """
        self.template_id = template_id
        self.name = name
        self.image_name = image_name
        self.container_disk_gb = container_disk_gb
        self.container_start_command = container_start_command
        return

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`RunpodPodTemplate` to a canonical API
            payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this pod template.
        """
        rtnval: Dict[str, Any] = {
            "id": self.template_id,
            "name": self.name,
            "imageName": self.image_name,
            "containerDiskInGb": self.container_disk_gb,
            "dockerArgs": self.container_start_command,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunpodPodTemplate":
        """
            Build a :class:`RunpodPodTemplate` from a RunPod API payload.

            :param data: The raw template dictionary.

            :returns: A populated :class:`RunpodPodTemplate`.
        """
        template_id = data.get("id")
        if template_id is None:
            template_id = data.get("template_id", "")

        name = data.get("name", "")

        image_name = data.get("imageName")
        if image_name is None:
            image_name = data.get("image_name", "")

        container_disk_gb = data.get("containerDiskInGb")
        if container_disk_gb is None:
            container_disk_gb = data.get("container_disk_gb", 10)

        container_start_command = data.get("dockerArgs")
        if container_start_command is None:
            container_start_command = data.get("container_start_command")

        rtnval = cls(template_id=template_id, name=name,
                     image_name=image_name,
                     container_disk_gb=container_disk_gb,
                     container_start_command=container_start_command)
        return rtnval


__all__ = ["RunpodPodTemplate"]

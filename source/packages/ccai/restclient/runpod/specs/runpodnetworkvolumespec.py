"""
    .. module:: runpodnetworkvolumespec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodNetworkVolumeSpec`
                   describing a network-volume create request.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict


class RunpodNetworkVolumeSpec:
    """
        A network-volume create request.

        Carries the volume name, the requested size in GiB, and the data
        center the volume must be provisioned in.
    """

    def __init__(self, *, name: str, size_gb: int,
                 data_center_id: str) -> None:
        """
            Initialize a :class:`RunpodNetworkVolumeSpec`.

            :param name: The volume name.
            :param size_gb: The requested volume size in GiB.
            :param data_center_id: The data center to provision in.

            :returns: ``None``.
        """
        self.name = name
        self.size_gb = size_gb
        self.data_center_id = data_center_id
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Render the spec into a RunPod API request body.

            :returns: A request-body dictionary.
        """
        rtnval: Dict[str, Any] = {
            "name": self.name,
            "size": self.size_gb,
            "dataCenterId": self.data_center_id,
        }
        return rtnval


__all__ = ["RunpodNetworkVolumeSpec"]

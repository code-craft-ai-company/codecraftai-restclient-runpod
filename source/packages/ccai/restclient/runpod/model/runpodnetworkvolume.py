"""
    .. module:: runpodnetworkvolume
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodNetworkVolume` model
                   describing a RunPod persistent network volume.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict


class RunpodNetworkVolume:
    """
        A RunPod persistent network volume.

        Carries the provider volume identifier, the volume name, the size in
        GiB, and the data center the volume is provisioned in.
    """

    def __init__(self, *, volume_id: str, name: str, size_gb: int,
                 data_center_id: str) -> None:
        """
            Initialize a :class:`RunpodNetworkVolume`.

            :param volume_id: The RunPod network-volume identifier.
            :param name: The volume name.
            :param size_gb: The volume size in GiB.
            :param data_center_id: The data center the volume lives in.

            :returns: ``None``.
        """
        self.volume_id = volume_id
        self.name = name
        self.size_gb = size_gb
        self.data_center_id = data_center_id
        return

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`RunpodNetworkVolume` to a canonical API
            payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this network volume.
        """
        rtnval: Dict[str, Any] = {
            "id": self.volume_id,
            "name": self.name,
            "size": self.size_gb,
            "dataCenterId": self.data_center_id,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunpodNetworkVolume":
        """
            Build a :class:`RunpodNetworkVolume` from a RunPod API payload.

            :param data: The raw network-volume dictionary.

            :returns: A populated :class:`RunpodNetworkVolume`.
        """
        volume_id = data.get("id")
        if volume_id is None:
            volume_id = data.get("volume_id", "")

        name = data.get("name", "")

        size_gb = data.get("size")
        if size_gb is None:
            size_gb = data.get("size_gb", 0)

        data_center_id = data.get("dataCenterId")
        if data_center_id is None:
            data_center_id = data.get("data_center_id", "")

        rtnval = cls(volume_id=volume_id, name=name, size_gb=size_gb,
                     data_center_id=data_center_id)
        return rtnval


__all__ = ["RunpodNetworkVolume"]

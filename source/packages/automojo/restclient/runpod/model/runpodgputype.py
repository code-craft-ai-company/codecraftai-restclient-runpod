"""
    .. module:: runpodgputype
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodGpuType` model
                   describing a RunPod GPU type catalog entry.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class RunpodGpuType:
    """
        A RunPod GPU type catalog entry.

        Carries the provider GPU type identifier, a display name, the
        per-card memory in GiB, and the lists of data centers that offer the
        GPU type as Secure Cloud and Community Cloud capacity.
    """

    def __init__(self, *, gpu_type_id: str, display_name: str,
                 memory_gb: int,
                 secure_data_centers: Optional[List[str]] = None,
                 community_data_centers: Optional[List[str]] = None) -> None:
        """
            Initialize a :class:`RunpodGpuType`.

            :param gpu_type_id: The RunPod GPU type identifier.
            :param display_name: A human-readable GPU model name.
            :param memory_gb: Per-card memory in GiB.
            :param secure_data_centers: Data centers offering Secure Cloud
                capacity for the GPU type.
            :param community_data_centers: Data centers offering Community
                Cloud capacity for the GPU type.

            :returns: ``None``.
        """
        self.gpu_type_id = gpu_type_id
        self.display_name = display_name
        self.memory_gb = memory_gb
        self.secure_data_centers: List[str] = []
        if secure_data_centers is not None:
            self.secure_data_centers = list(secure_data_centers)
        self.community_data_centers: List[str] = []
        if community_data_centers is not None:
            self.community_data_centers = list(community_data_centers)
        return

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`RunpodGpuType` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this GPU type.
        """
        rtnval: Dict[str, Any] = {
            "id": self.gpu_type_id,
            "displayName": self.display_name,
            "memoryInGb": self.memory_gb,
            "secureDataCenters": list(self.secure_data_centers),
            "communityDataCenters": list(self.community_data_centers),
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunpodGpuType":
        """
            Build a :class:`RunpodGpuType` from a RunPod API payload.

            :param data: The raw GPU type dictionary.

            :returns: A populated :class:`RunpodGpuType`.
        """
        gpu_type_id = data.get("id")
        if gpu_type_id is None:
            gpu_type_id = data.get("gpuTypeId", "")

        display_name = data.get("displayName")
        if display_name is None:
            display_name = data.get("name", "")

        memory_gb = data.get("memoryInGb")
        if memory_gb is None:
            memory_gb = data.get("memory_gb", 0)

        secure = data.get("secureDataCenters")
        if secure is None:
            secure = data.get("secure_data_centers", [])

        community = data.get("communityDataCenters")
        if community is None:
            community = data.get("community_data_centers", [])

        rtnval = cls(gpu_type_id=gpu_type_id, display_name=display_name,
                     memory_gb=memory_gb, secure_data_centers=secure,
                     community_data_centers=community)
        return rtnval


__all__ = ["RunpodGpuType"]

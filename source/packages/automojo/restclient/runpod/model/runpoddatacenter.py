"""
    .. module:: runpoddatacenter
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodDataCenter` model
                   describing a RunPod data-center catalog entry.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict


class RunpodDataCenter:
    """
        A RunPod data-center catalog entry.

        Carries the provider data-center identifier, a human-readable name,
        and a flag indicating whether the data center is part of RunPod's
        Secure Cloud.
    """

    def __init__(self, *, data_center_id: str, name: str,
                 secure_cloud: bool) -> None:
        """
            Initialize a :class:`RunpodDataCenter`.

            :param data_center_id: The RunPod data-center identifier.
            :param name: A human-readable data-center name.
            :param secure_cloud: Whether the data center is Secure Cloud.

            :returns: ``None``.
        """
        self.data_center_id = data_center_id
        self.name = name
        self.secure_cloud = secure_cloud
        return

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`RunpodDataCenter` to a canonical API
            payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this data center.
        """
        rtnval: Dict[str, Any] = {
            "id": self.data_center_id,
            "name": self.name,
            "secureCloud": self.secure_cloud,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunpodDataCenter":
        """
            Build a :class:`RunpodDataCenter` from a RunPod API payload.

            :param data: The raw data-center dictionary.

            :returns: A populated :class:`RunpodDataCenter`.
        """
        data_center_id = data.get("id")
        if data_center_id is None:
            data_center_id = data.get("data_center_id", "")

        name = data.get("name", "")

        secure_cloud = data.get("secureCloud")
        if secure_cloud is None:
            secure_cloud = data.get("secure_cloud", False)

        rtnval = cls(data_center_id=data_center_id, name=name,
                     secure_cloud=bool(secure_cloud))
        return rtnval


__all__ = ["RunpodDataCenter"]

"""
    .. module:: gputypesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`GpuTypesGroup` api group
                   exposing the RunPod GPU-type catalog endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.runpod.aspectsrunpod import (
    AspectsRunpod, DEFAULT_RUNPOD_ASPECTS
)
from ccai.restclient.runpod.apigroups.groupsupport import raise_for_status
from ccai.restclient.runpod.model.runpodgputype import RunpodGpuType


class GpuTypesGroup(RestApiGroup):
    """
        :class:`GpuTypesGroup` exposes the RunPod GPU-type catalog endpoint.
        The catalog is a small, non-paged collection.
    """

    BASE_LEAF = "/v1"

    def list(self, *,
             aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodGpuType]:
        """
            List every GPU type RunPod offers.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodGpuType` records.
        """
        client = self.client
        leaf = self.build_leaf(parts=["gpuTypes"])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="list gpu types")

        payload = response.json()
        raw_entries = self._extract_entries(payload=payload)

        rtnval: List[RunpodGpuType] = []
        for entry in raw_entries:
            rtnval.append(RunpodGpuType.from_dict(entry))

        return rtnval

    def _extract_entries(self, *, payload: Any) -> List[Dict[str, Any]]:
        """
            Extract the GPU-type entry list from a response payload.

            :param payload: The decoded response payload.

            :returns: The list of raw GPU-type dictionaries.
        """
        if isinstance(payload, list):
            rtnval: List[Dict[str, Any]] = list(payload)
            return rtnval

        if isinstance(payload, dict):
            entries = payload.get("gpuTypes")
            if entries is None:
                entries = payload.get("items", [])
            rtnval = list(entries)
            return rtnval

        rtnval = []
        return rtnval


__all__ = ["GpuTypesGroup"]

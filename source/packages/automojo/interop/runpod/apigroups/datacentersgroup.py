"""
    .. module:: datacentersgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`DataCentersGroup` api
                   group exposing the RunPod data-center catalog endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.runpod.aspectsrunpod import (
    AspectsRunpod, DEFAULT_RUNPOD_ASPECTS
)
from automojo.interop.runpod.apigroups.groupsupport import raise_for_status
from automojo.interop.runpod.model.runpoddatacenter import RunpodDataCenter


class DataCentersGroup(RestApiGroup):
    """
        :class:`DataCentersGroup` exposes the RunPod data-center catalog
        endpoint. The catalog is a small, non-paged collection.
    """

    BASE_LEAF = "/v1"

    def list(self, *,
             aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodDataCenter]:
        """
            List every RunPod data center.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodDataCenter` records.
        """
        client = self.client
        leaf = self.build_leaf(parts=["datacenters"])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="list data centers")

        payload = response.json()
        raw_entries = self._extract_entries(payload=payload)

        rtnval: List[RunpodDataCenter] = []
        for entry in raw_entries:
            rtnval.append(RunpodDataCenter.from_dict(entry))

        return rtnval

    def _extract_entries(self, *, payload: Any) -> List[Dict[str, Any]]:
        """
            Extract the data-center entry list from a response payload.

            :param payload: The decoded response payload.

            :returns: The list of raw data-center dictionaries.
        """
        if isinstance(payload, list):
            rtnval: List[Dict[str, Any]] = list(payload)
            return rtnval

        if isinstance(payload, dict):
            entries = payload.get("dataCenters")
            if entries is None:
                entries = payload.get("datacenters")
            if entries is None:
                entries = payload.get("items", [])
            rtnval = list(entries)
            return rtnval

        rtnval = []
        return rtnval


__all__ = ["DataCentersGroup"]

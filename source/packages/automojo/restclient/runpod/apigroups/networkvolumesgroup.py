"""
    .. module:: networkvolumesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`NetworkVolumesGroup` api
                   group exposing the RunPod network-volume endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.runpod.aspectsrunpod import (
    AspectsRunpod, DEFAULT_RUNPOD_ASPECTS
)
from automojo.restclient.runpod.apigroups.groupsupport import (
    iter_cursor_pages, raise_for_status, safe_json
)
from automojo.restclient.runpod.model.runpodnetworkvolume import (
    RunpodNetworkVolume
)
from automojo.restclient.runpod.specs.runpodnetworkvolumespec import (
    RunpodNetworkVolumeSpec
)


class NetworkVolumesGroup(RestApiGroup):
    """
        :class:`NetworkVolumesGroup` exposes the RunPod network-volume
        endpoints — idempotent create, cursor-paged list, and idempotent
        delete.
    """

    BASE_LEAF = "/v1"

    def create(self, *, spec: RunpodNetworkVolumeSpec,
               aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodNetworkVolume:
        """
            Create a network volume. An existing volume carrying the same
            name in the same data center is returned unchanged (idempotent
            create).

            :param spec: The :class:`RunpodNetworkVolumeSpec` to realise.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodNetworkVolume` record.

            :raises: :class:`SemanticError` when ``spec`` is ``None``.
        """
        if spec is None:
            raise SemanticError("NetworkVolumesGroup.create requires a spec.")

        existing = self._find_by_name(name=spec.name,
                                      data_center_id=spec.data_center_id,
                                      aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        leaf = self.build_leaf(parts=["networkvolumes"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(),
                                  aspects=aspects)
        raise_for_status(response=response, action="create network volume")

        rtnval = RunpodNetworkVolume.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *,
             aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodNetworkVolume]:
        """
            List every network volume, following cursor pages transparently.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodNetworkVolume` records.
        """
        client = self.client
        leaf = self.build_leaf(parts=["networkvolumes"])

        def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {"limit": str(aspects.page_size)}
            if cursor is not None:
                params["cursor"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list network volumes")
            page = safe_json(response=response)
            return page

        rtnval: List[RunpodNetworkVolume] = []
        for entry in iter_cursor_pages(fetch_page=fetch_page):
            rtnval.append(RunpodNetworkVolume.from_dict(entry))

        return rtnval

    def delete(self, *, volume_id: str,
               aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Delete a network volume. Deleting an unknown id is a no-op.

            :param volume_id: The network-volume identifier to delete.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``volume_id`` is empty.
        """
        if volume_id is None or len(volume_id) == 0:
            raise SemanticError("'volume_id' must be a non-empty string.")

        client = self.client
        leaf = self.build_leaf(parts=["networkvolumes", volume_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete network volume")
        return

    def _find_by_name(self, *, name: str, data_center_id: str,
                       aspects: AspectsRunpod) -> Optional[RunpodNetworkVolume]:
        """
            Find an existing network volume by name and data center.

            :param name: The volume name to match.
            :param data_center_id: The data center to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`RunpodNetworkVolume`, or ``None``.
        """
        volumes = self.list(aspects=aspects)
        for volume in volumes:
            if volume.name == name:
                if volume.data_center_id == data_center_id:
                    rtnval: Optional[RunpodNetworkVolume] = volume
                    return rtnval

        rtnval = None
        return rtnval


__all__ = ["NetworkVolumesGroup"]

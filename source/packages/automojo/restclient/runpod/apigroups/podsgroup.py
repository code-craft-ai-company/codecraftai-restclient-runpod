"""
    .. module:: podsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`PodsGroup` api group
                   exposing the RunPod pod-lifecycle endpoints.

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
from automojo.restclient.runpod.model.runpodpod import RunpodPod
from automojo.restclient.runpod.specs.runpodpodlaunchspec import (
    RunpodPodLaunchSpec
)


class PodsGroup(RestApiGroup):
    """
        :class:`PodsGroup` exposes the RunPod pod-lifecycle endpoints —
        launch, get, cursor-paged list, start, stop, and idempotent
        terminate.
    """

    BASE_LEAF = "/v1"

    def launch(self, *, spec: RunpodPodLaunchSpec,
               aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Launch a new pod from a :class:`RunpodPodLaunchSpec`.

            :param spec: The pod launch specification.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodPod` record.

            :raises: :class:`SemanticError` when ``spec`` is ``None``.
        """
        if spec is None:
            raise SemanticError("PodsGroup.launch requires a spec.")

        client = self.client
        leaf = self.build_leaf(parts=["pods"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(),
                                  aspects=aspects)
        raise_for_status(response=response, action="launch pod")

        rtnval = RunpodPod.from_dict(safe_json(response=response))
        return rtnval

    def get(self, *, pod_id: str,
            aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Retrieve a single pod's current state.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodPod` record.

            :raises: :class:`SemanticError` when ``pod_id`` is empty.
        """
        self._require_pod_id(pod_id=pod_id)

        client = self.client
        leaf = self.build_leaf(parts=["pods", pod_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get pod")

        rtnval = RunpodPod.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *,
             aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodPod]:
        """
            List every pod, following cursor pages transparently.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodPod` records.
        """
        client = self.client
        leaf = self.build_leaf(parts=["pods"])

        def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {"limit": str(aspects.page_size)}
            if cursor is not None:
                params["cursor"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list pods")
            page = safe_json(response=response)
            return page

        rtnval: List[RunpodPod] = []
        for entry in iter_cursor_pages(fetch_page=fetch_page):
            rtnval.append(RunpodPod.from_dict(entry))

        return rtnval

    def start(self, *, pod_id: str,
              aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Start a stopped pod.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`RunpodPod` record.

            :raises: :class:`SemanticError` when ``pod_id`` is empty.
        """
        rtnval = self._lifecycle_post(pod_id=pod_id, verb="start",
                                      aspects=aspects)
        return rtnval

    def stop(self, *, pod_id: str,
             aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Stop a running pod.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`RunpodPod` record.

            :raises: :class:`SemanticError` when ``pod_id`` is empty.
        """
        rtnval = self._lifecycle_post(pod_id=pod_id, verb="stop",
                                      aspects=aspects)
        return rtnval

    def terminate(self, *, pod_id: str,
                  aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Terminate a pod. Terminating an already-terminated pod is a
            no-op.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``pod_id`` is empty.
        """
        self._require_pod_id(pod_id=pod_id)

        client = self.client
        leaf = self.build_leaf(parts=["pods", pod_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="terminate pod")
        return

    def _lifecycle_post(self, *, pod_id: str, verb: str,
                        aspects: AspectsRunpod) -> RunpodPod:
        """
            POST a pod lifecycle verb (``start`` / ``stop``).

            :param pod_id: The pod identifier.
            :param verb: The lifecycle verb path segment.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`RunpodPod` record.
        """
        self._require_pod_id(pod_id=pod_id)

        client = self.client
        leaf = self.build_leaf(parts=["pods", pod_id, verb])
        response = client.request(method="POST", leaf=leaf, aspects=aspects)
        raise_for_status(response=response,
                         action="{} pod".format(verb))

        rtnval = RunpodPod.from_dict(safe_json(response=response))
        return rtnval

    def _require_pod_id(self, *, pod_id: str) -> None:
        """
            Validate a pod identifier argument.

            :param pod_id: The pod identifier to check.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``pod_id`` is empty.
        """
        if pod_id is None:
            raise SemanticError("'pod_id' must be a non-empty string.")
        if len(pod_id) == 0:
            raise SemanticError("'pod_id' must be a non-empty string.")
        return


__all__ = ["PodsGroup"]

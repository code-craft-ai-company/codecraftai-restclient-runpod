"""
    .. module:: podtemplatesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`PodTemplatesGroup` api
                   group exposing the RunPod pod-template endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.runpod.aspectsrunpod import (
    AspectsRunpod, DEFAULT_RUNPOD_ASPECTS
)
from ccai.restclient.runpod.apigroups.groupsupport import (
    iter_cursor_pages, raise_for_status, safe_json
)
from ccai.restclient.runpod.model.runpodpodtemplate import RunpodPodTemplate
from ccai.restclient.runpod.specs.runpodpodtemplatespec import (
    RunpodPodTemplateSpec
)


class PodTemplatesGroup(RestApiGroup):
    """
        :class:`PodTemplatesGroup` exposes the RunPod pod-template endpoints
        — cursor-paged list, idempotent create, and idempotent delete.
    """

    BASE_LEAF = "/v1"

    def list(self, *,
             aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodPodTemplate]:
        """
            List every pod template, following cursor pages transparently.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodPodTemplate` records.
        """
        client = self.client
        leaf = self.build_leaf(parts=["templates"])

        def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {"limit": str(aspects.page_size)}
            if cursor is not None:
                params["cursor"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list pod templates")
            page = safe_json(response=response)
            return page

        rtnval: List[RunpodPodTemplate] = []
        for entry in iter_cursor_pages(fetch_page=fetch_page):
            rtnval.append(RunpodPodTemplate.from_dict(entry))

        return rtnval

    def create(self, *, spec: RunpodPodTemplateSpec,
               aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPodTemplate:
        """
            Create a pod template. An existing template carrying the same
            name is returned unchanged (idempotent create).

            :param spec: The :class:`RunpodPodTemplateSpec` to realise.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodPodTemplate` record.

            :raises: :class:`SemanticError` when ``spec`` is ``None``.
        """
        if spec is None:
            raise SemanticError("PodTemplatesGroup.create requires a spec.")

        existing = self._find_by_name(name=spec.name, aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        leaf = self.build_leaf(parts=["templates"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(),
                                  aspects=aspects)
        raise_for_status(response=response, action="create pod template")

        rtnval = RunpodPodTemplate.from_dict(safe_json(response=response))
        return rtnval

    def delete(self, *, template_id: str,
               aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Delete a pod template. Deleting an unknown id is a no-op.

            :param template_id: The template identifier to delete.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``template_id`` is empty.
        """
        if template_id is None or len(template_id) == 0:
            raise SemanticError("'template_id' must be a non-empty string.")

        client = self.client
        leaf = self.build_leaf(parts=["templates", template_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete pod template")
        return

    def _find_by_name(self, *, name: str,
                       aspects: AspectsRunpod) -> Optional[RunpodPodTemplate]:
        """
            Find an existing pod template by name.

            :param name: The template name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`RunpodPodTemplate`, or ``None``.
        """
        templates = self.list(aspects=aspects)
        for template in templates:
            if template.name == name:
                rtnval: Optional[RunpodPodTemplate] = template
                return rtnval

        rtnval = None
        return rtnval


__all__ = ["PodTemplatesGroup"]

"""
    .. module:: tagsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TagsGroup` api group
                   exposing the RunPod resource-tagging endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.runpod.aspectsrunpod import (
    AspectsRunpod, DEFAULT_RUNPOD_ASPECTS
)
from ccai.restclient.runpod.apigroups.groupsupport import raise_for_status


# Resource types the RunPod tag endpoint accepts as a path segment.
_SUPPORTED_RESOURCE_TYPES = ("pods", "templates", "networkvolumes")


class TagsGroup(RestApiGroup):
    """
        :class:`TagsGroup` exposes the RunPod resource-tagging endpoint. A
        tag set is applied wholesale through a PATCH against the resource.
    """

    BASE_LEAF = "/v1"

    def apply(self, *, resource_type: str, resource_id: str,
              tags: Dict[str, str],
              aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Apply a tag set to a resource.

            :param resource_type: One of ``pods`` / ``templates`` /
                ``networkvolumes``.
            :param resource_id: The resource identifier.
            :param tags: The tag set to apply.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``resource_type`` is not a
                supported value or ``resource_id`` is empty.
        """
        if resource_type not in _SUPPORTED_RESOURCE_TYPES:
            err_msg = ("'resource_type' must be one of {}.".format(
                ", ".join(_SUPPORTED_RESOURCE_TYPES)))
            raise SemanticError(err_msg)
        if resource_id is None or len(resource_id) == 0:
            raise SemanticError("'resource_id' must be a non-empty string.")
        if tags is None:
            raise SemanticError("'tags' must be a dictionary.")

        client = self.client
        leaf = self.build_leaf(parts=[resource_type, resource_id])
        body: Dict[str, Any] = {"tags": dict(tags)}
        response = client.request(method="PATCH", leaf=leaf,
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="apply tags")
        return


__all__ = ["TagsGroup"]

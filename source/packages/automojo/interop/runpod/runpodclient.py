"""
    .. module:: runpodclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodClient` REST client
                   for the RunPod GPU-cloud API (``rest.runpod.io/v1``).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import json
import os
import time

from typing import Any, Dict, List, Optional, Union

from requests import Response, Session

from automojo.errors.exceptions import ConfigurationError, SemanticError

from automojo.credentials.basecredential import BaseCredential
from automojo.credentials.runpodapikeycredential import RunpodApiKeyCredential

from automojo.restclient.base.restclientbase import RestClientBase

from automojo.interop.runpod.aspectsrunpod import (
    AspectsRunpod, DEFAULT_RUNPOD_ASPECTS
)
from automojo.interop.runpod.apigroups.gputypesgroup import GpuTypesGroup
from automojo.interop.runpod.apigroups.datacentersgroup import DataCentersGroup
from automojo.interop.runpod.apigroups.podtemplatesgroup import (
    PodTemplatesGroup
)
from automojo.interop.runpod.apigroups.networkvolumesgroup import (
    NetworkVolumesGroup
)
from automojo.interop.runpod.apigroups.podsgroup import PodsGroup
from automojo.interop.runpod.apigroups.tagsgroup import TagsGroup
from automojo.interop.runpod.exceptions.runpoderrors import (
    RunpodAcceleratorNotAvailableError, RunpodCapacityUnavailableError,
    RunpodPodFailedError
)
from automojo.interop.runpod.enums.runpodcloudtype import RunpodCloudType
from automojo.interop.runpod.model.runpodgputype import RunpodGpuType
from automojo.interop.runpod.model.runpoddatacenter import RunpodDataCenter
from automojo.interop.runpod.model.runpodpodtemplate import RunpodPodTemplate
from automojo.interop.runpod.model.runpodnetworkvolume import (
    RunpodNetworkVolume
)
from automojo.interop.runpod.model.runpodpod import RunpodPod
from automojo.interop.runpod.specs.runpodpodtemplatespec import (
    RunpodPodTemplateSpec
)
from automojo.interop.runpod.specs.runpodnetworkvolumespec import (
    RunpodNetworkVolumeSpec
)
from automojo.interop.runpod.specs.runpodpodlaunchspec import (
    RunpodPodLaunchSpec
)


RUNPOD_API_HOST = "rest.runpod.io"


class RunpodClient(RestClientBase):
    """
        :class:`RunpodClient` is the typed, aspect-driven REST client for the
        RunPod GPU-cloud API. It is built on :class:`RestClientBase` and
        targets the newer REST surface at ``rest.runpod.io/v1``.

        RunPod is container-shaped: the API surface is GPU types, data
        centers, pod templates, network volumes, and pods. The client
        exposes that surface through six api groups (:attr:`gpu_types`,
        :attr:`data_centers`, :attr:`pod_templates`, :attr:`network_volumes`,
        :attr:`pods`, :attr:`tags`) plus convenience facade methods and a
        :meth:`wait_until_running` pod waiter.

        Authentication is Bearer-token, sourced from the supplied
        :class:`RunpodApiKeyCredential`. All HTTP behaviour is carried by
        :class:`AspectsRunpod`; no behaviour-modifying decorators are used.
    """

    def __init__(self, *, credential: BaseCredential,
                 host: str = RUNPOD_API_HOST,
                 aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Initialize the RunPod REST client.

            :param credential: A :class:`RunpodApiKeyCredential`.
            :param host: Override host name for the REST endpoint.
            :param aspects: Default :class:`AspectsRunpod` applied when a
                call omits an explicit aspects argument.

            :returns: ``None``.

            :raises: :class:`ConfigurationError` when ``credential`` is not a
                :class:`RunpodApiKeyCredential` or carries no token.
        """
        if not isinstance(credential, RunpodApiKeyCredential):
            err_msg_lines = ["RunpodClient requires a RunpodApiKeyCredential."]
            err_msg_lines.append("EXPECTED: RunpodApiKeyCredential")
            err_msg_lines.append("FOUND: {}".format(type(credential).__name__))
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        token = credential.token
        if token is None or len(token) == 0:
            err_msg_lines = ["RunpodClient credential carries no API token."]
            err_msg_lines.append("Provide a RunpodApiKeyCredential with a "
                                 "non-empty token.")
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        super().__init__(host=host, credential=credential, aspects=aspects)

        self._token = token

        self._gpu_types = GpuTypesGroup(self)
        self._data_centers = DataCentersGroup(self)
        self._pod_templates = PodTemplatesGroup(self)
        self._network_volumes = NetworkVolumesGroup(self)
        self._pods = PodsGroup(self)
        self._tags = TagsGroup(self)
        return

    # ------------------------------------------------------------------
    # API group accessors
    # ------------------------------------------------------------------

    @property
    def gpu_types(self) -> GpuTypesGroup:
        """
            The GPU-types api group.

            :returns: The :class:`GpuTypesGroup` instance.
        """
        rtnval = self._gpu_types
        return rtnval

    @property
    def data_centers(self) -> DataCentersGroup:
        """
            The data-centers api group.

            :returns: The :class:`DataCentersGroup` instance.
        """
        rtnval = self._data_centers
        return rtnval

    @property
    def pod_templates(self) -> PodTemplatesGroup:
        """
            The pod-templates api group.

            :returns: The :class:`PodTemplatesGroup` instance.
        """
        rtnval = self._pod_templates
        return rtnval

    @property
    def network_volumes(self) -> NetworkVolumesGroup:
        """
            The network-volumes api group.

            :returns: The :class:`NetworkVolumesGroup` instance.
        """
        rtnval = self._network_volumes
        return rtnval

    @property
    def pods(self) -> PodsGroup:
        """
            The pods api group.

            :returns: The :class:`PodsGroup` instance.
        """
        rtnval = self._pods
        return rtnval

    @property
    def tags(self) -> TagsGroup:
        """
            The tags api group.

            :returns: The :class:`TagsGroup` instance.
        """
        rtnval = self._tags
        return rtnval

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def request(self, *, method: str, leaf: str,
                params: Optional[Dict[str, str]] = None,
                json_body: Optional[Union[Dict[str, Any], list]] = None,
                headers: Optional[Dict[str, str]] = None,
                aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> Response:
        """
            Issue a single REST call against the RunPod API.

            The call attaches the Bearer token and serializes ``json_body``
            as raw JSON. HTTP-status reclassification is delegated to the
            api-group helpers; this method only performs the send.

            :param method: HTTP method to invoke.
            :param leaf: API leaf path beginning with ``/``.
            :param params: Optional query-string parameters.
            :param json_body: Optional dict/list serialized as the body.
            :param headers: Optional additional request headers.
            :param aspects: Behaviour-control aspects for the call.

            :returns: The :class:`Response` object from the call.
        """
        session = self._authenticated_session(aspects=aspects)

        call_url = self._format_call_url(leaf)
        send_timeouts = (aspects.connection_timeout,
                         aspects.inactivity_timeout)

        send_headers: Dict[str, str] = {}
        if headers is not None:
            send_headers.update(headers)

        body_bytes: Optional[bytes] = None
        if json_body is not None:
            body_bytes = json.dumps(json_body).encode("utf-8")
            if "Content-Type" not in send_headers:
                send_headers["Content-Type"] = "application/json"

        response: Response = session.request(method=method, url=call_url,
                                              params=params, data=body_bytes,
                                              headers=send_headers,
                                              timeout=send_timeouts,
                                              verify=self._verify_certificate)
        rtnval = response
        return rtnval

    def _authenticated_session(self, *, aspects: AspectsRunpod) -> Session:
        """
            Build a :class:`Session` carrying the Bearer token.

            :param aspects: Behaviour-control aspects. An aspects-supplied
                session is honoured when present.

            :returns: A :class:`Session` ready to issue authenticated calls.
        """
        if aspects.session is not None:
            rtnval = aspects.session
            return rtnval

        session = Session()
        session.verify = self._verify_certificate
        session.headers.update({
            "Authorization": "Bearer {}".format(self._token),
            "Accept": "application/json",
        })

        rtnval = session
        return rtnval

    # ------------------------------------------------------------------
    # Facade methods
    # ------------------------------------------------------------------

    def list_gpu_types(self, *,
                        aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodGpuType]:
        """
            Enumerate every GPU type RunPod offers.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodGpuType` records.
        """
        rtnval = self._gpu_types.list(aspects=aspects)
        return rtnval

    def list_data_centers(self, *,
                          aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodDataCenter]:
        """
            Enumerate every RunPod data center.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodDataCenter` records.
        """
        rtnval = self._data_centers.list(aspects=aspects)
        return rtnval

    def list_pod_templates(self, *,
                           aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodPodTemplate]:
        """
            Enumerate every pod template.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodPodTemplate` records.
        """
        rtnval = self._pod_templates.list(aspects=aspects)
        return rtnval

    def create_pod_template(self, *, spec: RunpodPodTemplateSpec,
                            aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPodTemplate:
        """
            Create a pod template (idempotent on name).

            :param spec: The :class:`RunpodPodTemplateSpec` to realise.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodPodTemplate` record.
        """
        rtnval = self._pod_templates.create(spec=spec, aspects=aspects)
        return rtnval

    def delete_pod_template(self, *, template_id: str,
                            aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Delete a pod template (no-op on an unknown id).

            :param template_id: The template identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        self._pod_templates.delete(template_id=template_id, aspects=aspects)
        return

    def create_network_volume(self, *, spec: RunpodNetworkVolumeSpec,
                              aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodNetworkVolume:
        """
            Create a network volume (idempotent on name + data center).

            :param spec: The :class:`RunpodNetworkVolumeSpec` to realise.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodNetworkVolume` record.
        """
        rtnval = self._network_volumes.create(spec=spec, aspects=aspects)
        return rtnval

    def list_network_volumes(self, *,
                             aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodNetworkVolume]:
        """
            Enumerate every network volume.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodNetworkVolume` records.
        """
        rtnval = self._network_volumes.list(aspects=aspects)
        return rtnval

    def delete_network_volume(self, *, volume_id: str,
                              aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Delete a network volume (no-op on an unknown id).

            :param volume_id: The network-volume identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        self._network_volumes.delete(volume_id=volume_id, aspects=aspects)
        return

    def launch_pod(self, *, spec: RunpodPodLaunchSpec,
                   aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Launch a pod from a :class:`RunpodPodLaunchSpec`.

            The requested GPU type must be available in at least one data
            center; Secure Cloud requests must additionally find Secure
            Cloud capacity for the GPU type.

            :param spec: The pod launch specification.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodPod` record.

            :raises: :class:`RunpodAcceleratorNotAvailableError` when the GPU
                type is not offered in any data center;
                :class:`RunpodCapacityUnavailableError` when Secure Cloud
                capacity for the GPU type is unavailable.
        """
        if spec is None:
            raise SemanticError("RunpodClient.launch_pod requires a spec.")

        self._check_capacity(spec=spec, aspects=aspects)

        rtnval = self._pods.launch(spec=spec, aspects=aspects)
        return rtnval

    def get_pod(self, *, pod_id: str,
                aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Retrieve a pod's current state.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`RunpodPod` record.
        """
        rtnval = self._pods.get(pod_id=pod_id, aspects=aspects)
        return rtnval

    def list_pods(self, *,
                  aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> List[RunpodPod]:
        """
            Enumerate every pod.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`RunpodPod` records.
        """
        rtnval = self._pods.list(aspects=aspects)
        return rtnval

    def start_pod(self, *, pod_id: str,
                  aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Start a stopped pod.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`RunpodPod` record.
        """
        rtnval = self._pods.start(pod_id=pod_id, aspects=aspects)
        return rtnval

    def stop_pod(self, *, pod_id: str,
                 aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Stop a running pod.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`RunpodPod` record.
        """
        rtnval = self._pods.stop(pod_id=pod_id, aspects=aspects)
        return rtnval

    def terminate_pod(self, *, pod_id: str,
                      aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> None:
        """
            Terminate a pod (no-op on an already-terminated pod).

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        self._pods.terminate(pod_id=pod_id, aspects=aspects)
        return

    def apply_tags(self, *, resource_type: str, resource_id: str,
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
        """
        self._tags.apply(resource_type=resource_type,
                         resource_id=resource_id, tags=tags, aspects=aspects)
        return

    # ------------------------------------------------------------------
    # Waiter
    # ------------------------------------------------------------------

    def wait_until_running(self, *, pod_id: str,
                           aspects: AspectsRunpod = DEFAULT_RUNPOD_ASPECTS) -> RunpodPod:
        """
            Poll :meth:`get_pod` until the pod reaches the running state.

            :param pod_id: The pod identifier.
            :param aspects: Behaviour control. ``pod_running_timeout_seconds``
                bounds the wait; ``pod_poll_interval_seconds`` sets the poll
                cadence.

            :returns: The :class:`RunpodPod` once it is running.

            :raises: :class:`RunpodPodFailedError` when the pod enters a
                terminal-failed state; :class:`TimeoutError` when the running
                state is not reached within the budget.
        """
        timeout = aspects.pod_running_timeout_seconds
        interval = aspects.pod_poll_interval_seconds
        start_time = time.time()

        while True:
            pod = self.get_pod(pod_id=pod_id, aspects=aspects)

            if pod.is_running is True:
                rtnval = pod
                return rtnval

            if pod.is_failed is True:
                err_msg_lines = ["RunPod pod entered a terminal-failed "
                                 "state while waiting for RUNNING."]
                err_msg_lines.append("POD: {}".format(pod_id))
                err_msg_lines.append("STATUS: {}".format(pod.desired_status))
                err_msg = os.linesep.join(err_msg_lines)
                raise RunpodPodFailedError(err_msg)

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                err_msg_lines = ["Timed out waiting for a RunPod pod to "
                                 "reach the RUNNING state."]
                err_msg_lines.append("POD: {}".format(pod_id))
                err_msg_lines.append("LAST STATUS: {}".format(
                    pod.desired_status))
                err_msg_lines.append("TIMEOUT: {}s".format(timeout))
                err_msg = os.linesep.join(err_msg_lines)
                raise TimeoutError(err_msg)

            time.sleep(interval)

    # ------------------------------------------------------------------
    # Capacity probe
    # ------------------------------------------------------------------

    def _check_capacity(self, *, spec: RunpodPodLaunchSpec,
                        aspects: AspectsRunpod) -> None:
        """
            Verify the requested GPU type has capacity for the launch spec.

            :param spec: The pod launch specification.
            :param aspects: Behaviour control for the catalog probe.

            :returns: ``None``.

            :raises: :class:`RunpodAcceleratorNotAvailableError` when the GPU
                type is not offered anywhere;
                :class:`RunpodCapacityUnavailableError` when a Secure Cloud
                request finds no Secure Cloud capacity for the GPU type.
        """
        gpu_types = self.list_gpu_types(aspects=aspects)

        matched: Optional[RunpodGpuType] = None
        for gpu_type in gpu_types:
            if gpu_type.gpu_type_id == spec.gpu_type_id:
                matched = gpu_type
                break

        if matched is None:
            err_msg_lines = ["The requested RunPod GPU type is not available "
                             "in any data center."]
            err_msg_lines.append("GPU TYPE: {}".format(spec.gpu_type_id))
            err_msg = os.linesep.join(err_msg_lines)
            raise RunpodAcceleratorNotAvailableError(err_msg)

        if spec.cloud_type == RunpodCloudType.SECURE:
            if len(matched.secure_data_centers) == 0:
                err_msg_lines = ["No Secure Cloud capacity is available for "
                                 "the requested RunPod GPU type."]
                err_msg_lines.append("GPU TYPE: {}".format(spec.gpu_type_id))
                err_msg_lines.append("Consider cloud_type=COMMUNITY.")
                err_msg = os.linesep.join(err_msg_lines)
                raise RunpodCapacityUnavailableError(err_msg)
        else:
            if len(matched.community_data_centers) == 0:
                err_msg_lines = ["No Community Cloud capacity is available "
                                 "for the requested RunPod GPU type."]
                err_msg_lines.append("GPU TYPE: {}".format(spec.gpu_type_id))
                err_msg = os.linesep.join(err_msg_lines)
                raise RunpodAcceleratorNotAvailableError(err_msg)

        return


__all__ = ["RunpodClient", "RUNPOD_API_HOST"]

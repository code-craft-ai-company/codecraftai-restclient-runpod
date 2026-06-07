"""
    .. module:: runpodpod
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodPod` model
                   describing a RunPod pod (container) and its runtime state.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


# RunPod desired-status values that indicate a terminal-failed pod.
RUNPOD_FAILED_STATUSES = ("FAILED", "TERMINATED", "EXITED")

# RunPod desired-status value that indicates a running pod.
RUNPOD_RUNNING_STATUS = "RUNNING"


class RunpodPort:
    """
        A single public-port mapping exposed by a running RunPod pod.
    """

    def __init__(self, *, private_port: int, public_port: int,
                 ip: Optional[str] = None,
                 protocol: str = "tcp") -> None:
        """
            Initialize a :class:`RunpodPort`.

            :param private_port: The in-container port.
            :param public_port: The publicly-reachable port.
            :param ip: The public IP the port is reachable on.
            :param protocol: The transport protocol (``tcp`` / ``http``).

            :returns: ``None``.
        """
        self.private_port = private_port
        self.public_port = public_port
        self.ip = ip
        self.protocol = protocol
        return

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`RunpodPort` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this port mapping.
        """
        rtnval: Dict[str, Any] = {
            "privatePort": self.private_port,
            "publicPort": self.public_port,
            "ip": self.ip,
            "type": self.protocol,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunpodPort":
        """
            Build a :class:`RunpodPort` from a RunPod API payload.

            :param data: The raw port dictionary.

            :returns: A populated :class:`RunpodPort`.
        """
        private_port = data.get("privatePort")
        if private_port is None:
            private_port = data.get("private_port", 0)

        public_port = data.get("publicPort")
        if public_port is None:
            public_port = data.get("public_port", 0)

        ip = data.get("ip")
        protocol = data.get("type")
        if protocol is None:
            protocol = data.get("protocol", "tcp")

        rtnval = cls(private_port=private_port, public_port=public_port,
                     ip=ip, protocol=protocol)
        return rtnval


class RunpodPod:
    """
        A RunPod pod (container) and its runtime state.

        Carries the provider pod identifier, the pod name, the desired
        status, the GPU type and count, the public-port mappings, and an
        optional runtime SSH endpoint.
    """

    def __init__(self, *, pod_id: str, name: str, desired_status: str,
                 gpu_type_id: str = "", gpu_count: int = 0,
                 image_name: str = "",
                 public_ip: Optional[str] = None,
                 ports: Optional[List[RunpodPort]] = None,
                 ssh_endpoint: Optional[str] = None) -> None:
        """
            Initialize a :class:`RunpodPod`.

            :param pod_id: The RunPod pod identifier.
            :param name: The pod name.
            :param desired_status: The RunPod desired-status value.
            :param gpu_type_id: The GPU type the pod runs on.
            :param gpu_count: The number of GPUs attached to the pod.
            :param image_name: The container image reference.
            :param public_ip: The public IP allocated to the pod.
            :param ports: The public-port mappings.
            :param ssh_endpoint: An optional runtime SSH endpoint string.

            :returns: ``None``.
        """
        self.pod_id = pod_id
        self.name = name
        self.desired_status = desired_status
        self.gpu_type_id = gpu_type_id
        self.gpu_count = gpu_count
        self.image_name = image_name
        self.public_ip = public_ip
        self.ports: List[RunpodPort] = []
        if ports is not None:
            self.ports = list(ports)
        self.ssh_endpoint = ssh_endpoint
        return

    @property
    def is_running(self) -> bool:
        """
            Whether the pod is in the RunPod running state.

            :returns: ``True`` when the desired status is ``RUNNING``.
        """
        rtnval = self.desired_status == RUNPOD_RUNNING_STATUS
        return rtnval

    @property
    def is_failed(self) -> bool:
        """
            Whether the pod is in a terminal-failed state.

            :returns: ``True`` when the desired status is terminal-failed.
        """
        rtnval = self.desired_status in RUNPOD_FAILED_STATUSES
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`RunpodPod` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.  Nested port mappings are
            serialized via :meth:`RunpodPort.to_dict`.

            :returns: A dictionary payload describing this pod.
        """
        port_payloads: List[Dict[str, Any]] = []
        for port in self.ports:
            port_payloads.append(port.to_dict())

        rtnval: Dict[str, Any] = {
            "id": self.pod_id,
            "name": self.name,
            "desiredStatus": self.desired_status,
            "gpuTypeId": self.gpu_type_id,
            "gpuCount": self.gpu_count,
            "imageName": self.image_name,
            "publicIp": self.public_ip,
            "portMappings": port_payloads,
            "sshEndpoint": self.ssh_endpoint,
        }
        return rtnval

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunpodPod":
        """
            Build a :class:`RunpodPod` from a RunPod API payload.

            :param data: The raw pod dictionary.

            :returns: A populated :class:`RunpodPod`.
        """
        pod_id = data.get("id")
        if pod_id is None:
            pod_id = data.get("pod_id", "")

        name = data.get("name", "")

        desired_status = data.get("desiredStatus")
        if desired_status is None:
            desired_status = data.get("desired_status", "PENDING")

        gpu_type_id = data.get("gpuTypeId")
        if gpu_type_id is None:
            gpu_type_id = data.get("gpu_type_id", "")

        gpu_count = data.get("gpuCount")
        if gpu_count is None:
            gpu_count = data.get("gpu_count", 0)

        image_name = data.get("imageName")
        if image_name is None:
            image_name = data.get("image_name", "")

        public_ip = data.get("publicIp")
        if public_ip is None:
            public_ip = data.get("public_ip")

        raw_ports = data.get("portMappings")
        if raw_ports is None:
            raw_ports = data.get("ports", [])
        ports: List[RunpodPort] = []
        for entry in raw_ports:
            ports.append(RunpodPort.from_dict(entry))

        ssh_endpoint = data.get("sshEndpoint")
        if ssh_endpoint is None:
            ssh_endpoint = data.get("ssh_endpoint")

        rtnval = cls(pod_id=pod_id, name=name,
                     desired_status=desired_status,
                     gpu_type_id=gpu_type_id, gpu_count=gpu_count,
                     image_name=image_name, public_ip=public_ip,
                     ports=ports, ssh_endpoint=ssh_endpoint)
        return rtnval


__all__ = ["RunpodPod", "RunpodPort", "RUNPOD_FAILED_STATUSES",
           "RUNPOD_RUNNING_STATUS"]

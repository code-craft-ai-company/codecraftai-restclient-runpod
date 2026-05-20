"""
    .. module:: runpoderrors
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the exception types raised by the
                   RunPod interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


class RunpodError(RuntimeError):
    """
        Base exception type for every RunPod interop client failure.
    """


class RunpodAuthenticationError(RunpodError):
    """
        Raised when the RunPod API rejects the supplied credential with an
        HTTP 401 or 403 response.
    """


class RunpodAcceleratorNotAvailableError(RunpodError):
    """
        Raised when a requested GPU type is not available in any RunPod
        data center.
    """


class RunpodCapacityUnavailableError(RunpodError):
    """
        Raised when the requested Secure Cloud capacity is unavailable in
        any RunPod data center.
    """


class RunpodPodFailedError(RunpodError):
    """
        Raised when a RunPod pod enters a terminal-failed state while a
        waiter is polling for the running state.
    """


__all__ = [
    "RunpodError",
    "RunpodAuthenticationError",
    "RunpodAcceleratorNotAvailableError",
    "RunpodCapacityUnavailableError",
    "RunpodPodFailedError",
]

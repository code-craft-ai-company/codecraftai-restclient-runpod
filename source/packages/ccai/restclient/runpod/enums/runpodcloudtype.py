"""
    .. module:: runpodcloudtype
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RunpodCloudType` enum
                   distinguishing Secure Cloud from Community Cloud capacity.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from enum import Enum


class RunpodCloudType(Enum):
    """
        Discriminator for the RunPod capacity tier a pod is launched into.

        SECURE    — vetted, RunPod-operated data centers.
        COMMUNITY — peered third-party providers (lower cost, less vetted).
    """

    SECURE = "SECURE"
    COMMUNITY = "COMMUNITY"


__all__ = ["RunpodCloudType"]

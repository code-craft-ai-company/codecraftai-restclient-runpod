=========================================
Automation Mojo Rest Client - RunPod
=========================================

The ``automojo-restclient-runpod`` package is the venue-specific REST client for RunPod, a
GPU cloud whose primary unit of provisioning is the container *pod* rather than the VM.
The provider exposes secure-cloud and community-cloud capacity tiers, pod templates,
GPU-type and region catalogs, persistent network volumes, and a small lifecycle surface
for pods. The container-first shape makes RunPod a natural ``WorkloadVenue`` rather than a
``CloudVenue`` in the neutral provisioning model.

Highlights
==========

- ``RunpodClient`` — a ``RestClientBase`` subclass covering authentication, GPU-type and pod-template enumeration, and region catalogs.
- Network-volume lifecycle — create, inspect, and delete persistent network volumes.
- Pod lifecycle — launch, inspect, stop, start, and terminate container pods across secure-cloud and community-cloud tiers.
- Scope boundary — multi-node training shapes are out of scope at the client level; the provisioner composes per-pod calls to express them.
- Aspects-driven transport — every behaviour-bearing call accepts ``aspects: AspectsRest = DEFAULT_RUNPOD_ASPECTS``; credentials enter as typed ``RunpodApiKeyCredential`` instances from ``automojo-credentials``.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/automojo/restclient/runpod/`` - Package source code.
- ``source/testroots/testbase/automojo/tests/restclient/runpod/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation (Kiro-style).
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

.. code-block:: bash

   source .venv/bin/activate
   PYTHONPATH=source/packages:source/testroots/testbase python -m pytest source/testroots -q

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``

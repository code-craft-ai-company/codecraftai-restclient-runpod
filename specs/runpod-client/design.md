# Design

## Overview

`RunpodClient` is a `RestClientBase` subclass that talks to the RunPod
REST API. The shape is container-first: GPU types, pod templates,
network volumes, and pods. There is no VPC/subnet/security-group layer
to model — RunPod handles networking implicitly.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  codecraftai-provisioning / venues / runpod               │
│  (WorkloadProvisioner lifecycle)                       │
└──────────┬─────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  RunpodClient                                          │
│   RestClientBase + AspectsRest                         │
│   API groups: gpu-types, data-centers, pod-templates,  │
│     network-volumes, pods, tags                        │
└──────────┬─────────────────────────────────────────────┘
           │ HTTPS, Bearer token
           ▼
┌────────────────────────────────────────────────────────┐
│  api.runpod.io                                         │
└────────────────────────────────────────────────────────┘
```

---

## Data Model

`model/`: `runpodgputype.py`, `runpoddatacenter.py`, `runpodpodtemplate.py`,
`runpodnetworkvolume.py`, `runpodpod.py`.

`specs/`: `runpodpodlaunchspec.py`, `runpodpodtemplatespec.py`,
`runpodnetworkvolumespec.py`.

Enums: `runpodcloudtype.py` (`SECURE`, `COMMUNITY`).

Exceptions: `RunpodAuthenticationError`,
`RunpodAcceleratorNotAvailableError`, `RunpodCapacityUnavailableError`,
`RunpodPodFailedError`.

---

## Module Layout

```
source/packages/ccai/restclient/runpod/
├── runpodclient.py
├── aspectsrunpod.py
├── apigroups/
├── model/
├── specs/
├── enums/
└── exceptions/
```

---

## See Also

- `codecraftai-restclient-base/specs/restapigroup-enhancements/`
- `codecraftai-provisioning/specs/venue-runpod/`
- `codecraftai-credentials/specs/runpod-credentials/`

---

## Testing Strategy

Example-based tests cover authentication, pod-template idempotent
create, network-volume idempotent create, pod launch + terminate,
secure vs community selection, and HTTP-error reclassification.

Property-based tests (hypothesis) are **required** for:
1. **Paging cursor traversal** across `list_*` endpoints.
2. **URL composition** — per-segment encoding, empty/`None` rejection.
3. **Idempotent retry semantics** within and beyond budget.
4. **`wait_until_running`** terminal-state correctness against arbitrary
   monotonic mock streams.

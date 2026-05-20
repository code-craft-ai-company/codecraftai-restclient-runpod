# Requirements

## Introduction

The `runpod-client` feature provides a REST client for RunPod, a
container-pod GPU cloud. The provisioning unit is the pod (container),
not a VM. This client exposes GPU type and pod template catalogs,
persistent (network) volumes, and the pod lifecycle (launch, inspect,
start, stop, terminate) needed by `venue-runpod` in
`automojo-provisioning`.

Transport is REST on `RestClientBase`. Authentication uses
`RunpodApiKeyCredential`. Every behaviour-bearing method accepts
`aspects: AspectsRest = DEFAULT_RUNPOD_ASPECTS`.

---

## Requirements

### Requirement 1: Authenticate

#### Acceptance Criteria

1. WHEN the client is constructed with a `RunpodApiKeyCredential` THE
   SYSTEM SHALL configure `RestClientBase` with Bearer-token auth.
2. WHEN the credential is missing or empty THE SYSTEM SHALL raise
   `ConfigurationError`.
3. WHEN HTTP 401/403 is returned THE SYSTEM SHALL reclassify into
   `RunpodAuthenticationError`.

### Requirement 2: Enumerate GPU Types and Regions

#### Acceptance Criteria

1. WHEN the caller invokes `list_gpu_types(aspects)` THE SYSTEM SHALL
   return `RunpodGpuType` records with model, memory, secure/community
   availability per data center.
2. WHEN the caller invokes `list_data_centers(aspects)` THE SYSTEM SHALL
   return `RunpodDataCenter` records.

### Requirement 3: Manage Pod Templates

#### Acceptance Criteria

1. WHEN the caller invokes `list_pod_templates(aspects)` THE SYSTEM SHALL
   return `RunpodPodTemplate` records.
2. WHEN the caller invokes `create_pod_template(spec, aspects)` THE
   SYSTEM SHALL POST and return a `RunpodPodTemplate`. An existing
   template with the same name SHALL be returned (idempotent create).
3. WHEN `delete_pod_template(template_id, aspects)` is called against an
   unknown id THE SYSTEM SHALL succeed as a no-op.

### Requirement 4: Manage Network Volumes (Persistent Storage)

#### Acceptance Criteria

1. WHEN the caller invokes `create_network_volume(spec, aspects)` THE
   SYSTEM SHALL POST and return a `RunpodNetworkVolume`. An existing
   volume with the same name in the same data center SHALL be returned
   (idempotent create).
2. WHEN the caller invokes `list_network_volumes(aspects)` THE SYSTEM
   SHALL follow paging cursors.
3. WHEN `delete_network_volume(volume_id, aspects)` is called against
   an unknown id THE SYSTEM SHALL succeed as a no-op.

### Requirement 5: Launch and Manage Pods

#### Acceptance Criteria

1. WHEN the caller invokes `launch_pod(spec, aspects)` where `spec` is a
   `RunpodPodLaunchSpec` (gpu_type, gpu_count, template_id, name,
   container_disk_gb, volume_mounts, ports, env, cloud_type) THE SYSTEM
   SHALL POST and return a `RunpodPod` record.
2. WHEN the spec requests a GPU type that is not available in any
   data center THE SYSTEM SHALL raise `RunpodAcceleratorNotAvailableError`.
3. WHEN the caller invokes `get_pod(pod_id, aspects)` THE SYSTEM SHALL
   return the current pod state including public ports and runtime ssh
   endpoint.
4. WHEN the caller invokes `start_pod(pod_id, aspects)` or
   `stop_pod(pod_id, aspects)` THE SYSTEM SHALL POST and return the
   updated `RunpodPod` record.
5. WHEN the caller invokes `terminate_pod(pod_id, aspects)` THE SYSTEM
   SHALL DELETE the pod. Terminating an already-terminated pod SHALL
   succeed as a no-op.
6. WHEN the caller invokes `list_pods(aspects)` THE SYSTEM SHALL follow
   paging cursors.

### Requirement 6: Cloud-Type Selection (Secure vs Community)

#### Acceptance Criteria

1. WHEN `RunpodPodLaunchSpec.cloud_type` is not one of `SECURE` or
   `COMMUNITY` THE SYSTEM SHALL raise `SemanticError`.
2. WHEN the spec asks for `SECURE` capacity that is unavailable in any
   data center THE SYSTEM SHALL raise `RunpodCapacityUnavailableError`.

### Requirement 7: Wait Until a Pod Is Running

#### Acceptance Criteria

1. WHEN the caller invokes `wait_until_running(pod_id, aspects)` THE
   SYSTEM SHALL poll `get_pod` at the interval dictated by aspects.
2. WHEN the timeout elapses THE SYSTEM SHALL raise `TimeoutError`.
3. WHEN the pod enters a terminal-failed state THE SYSTEM SHALL raise
   `RunpodPodFailedError`.

### Requirement 8: Tagging

#### Acceptance Criteria

1. WHEN the caller invokes `apply_tags(resource_type, resource_id, tags, aspects)`
   THE SYSTEM SHALL PATCH the resource with the supplied tag set.

### Requirement 9: URL Composition

#### Acceptance Criteria

1. Per-segment percent-encoding; empty/`None` identifiers raise
   `SemanticError`.

### Requirement 10: Aspects on Every Behaviour-Bearing Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRest = DEFAULT_RUNPOD_ASPECTS`
   as a named-only parameter on every I/O method; no behaviour-modifying
   decorators.

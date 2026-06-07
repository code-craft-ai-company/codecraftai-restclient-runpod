# Implementation Plan — RunPod Client

## Package Skeleton

- [x] 1. Create `source/packages/ccai/restclient/runpod/` package tree.
- [x] 2. Add `aspectsrunpod.py` with `DEFAULT_RUNPOD_ASPECTS`.

## Client Core

- [x] 3. Implement `RunpodClient(RestClientBase)` with Bearer-token auth.
- [x] 4. Implement URL composition helper.
- [x] 5. Implement HTTP-error reclassification.

## Data Model, Specs, Enums

- [x] 6. Implement model dataclasses for GPU type, data center, pod template, network volume, pod.
- [x] 7. Implement spec dataclasses for pod launch, pod template, network volume.
- [x] 8. Implement `RunpodCloudType` enum (`SECURE`/`COMMUNITY`).

## API Groups

- [x] 9. Implement `GpuTypesGroup.list`.
- [x] 10. Implement `DataCentersGroup.list`.
- [x] 11. Implement `PodTemplatesGroup.list/create/delete` with idempotency.
- [x] 12. Implement `NetworkVolumesGroup.create/list/delete` with idempotency.
- [x] 13. Implement `PodsGroup.launch/get/list/start/stop/terminate`.
- [x] 14. Implement `TagsGroup.apply`.

## Waiters

- [x] 15. Implement `wait_until_running(pod_id, aspects)`.

## Paging

- [x] 16. Transparent cursor traversal for every `list_*`.

## Tests — Example-Based

- [x] 17. Construction + authentication tests.
- [x] 18. Idempotent template/volume create tests.
- [x] 19. Pod launch + terminate happy path.
- [x] 20. Secure vs community selection tests.
- [x] 21. HTTP-error reclassification.

## Tests — Property-Based (hypothesis)

- [x] 22. Paging traversal totality.
- [x] 23. URL composition determinism + per-segment encoding + rejection.
- [x] 24. Idempotent-retry equivalence.
- [x] 25. `wait_until_running` terminal-state correctness.

## Integration

- [ ] 26. Smoke-test fixture for live RunPod API.

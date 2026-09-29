# Unsupported deployment note

CourtSight does not currently provide a verified hosted deployment workflow.
The supported deliverable is the local Flask/React demo documented in the
repository root [README](../README.md).

In particular, deploying only this Python directory will not produce the UI:
`frontend/dist` must be built first, and model weights must be supplied
manually.

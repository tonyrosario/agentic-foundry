# Template: authoritative source bundle

## Purpose

Bind every artifact that defines, constrains, supports, or disputes the intended outcome into one immutable, ordered source set. Downstream lifecycle records reference this bundle rather than collapsing intent to one ticket or document.

## Record

```yaml
schema_version: "1.0"
source_bundle_id: "source-bundle-..."
source_bundle_version: "..."
status: "active" # draft | active | disputed | superseded
created_at: "..."
created_by: "..."

artifacts:
  - source_artifact_id: "ticket"
    kind: "ticket" # ticket | prd | acceptance-criteria | adr | policy | approved-decision | contract | supporting-document
    path_or_uri: "..."
    sha256: "..."
    authority: "authoritative" # authoritative | supporting | disputed
    read_order: 1
    precedence_rank: 1
    effective_at: null
    supersedes_source_artifact_ids: []
    requirement_ids: []

conflicts:
  - conflict_id: "..."
    source_artifact_ids: []
    description: "..."
    materiality: "high"
    status: "unresolved" # unresolved | resolved
    resolution_decision_id: null
    resolution_decision_record_version: null
    resolution_decision_record_schema_version: null
    resolution_decision_record_sha256: null

integrity:
  hash_profile: "canonical-json-sha256-v1"
  source_bundle_sha256: "..."
  supersedes_source_bundle_id: null
  supersedes_source_bundle_sha256: null
```

## Rules

- Include every artifact that defines an outcome, acceptance criterion, constraint, non-goal, or approved source decision.
- Retain supporting and disputed artifacts with explicit authority labels; do not silently discard inconvenient conflicts.
- `read_order` controls source-first review order. `precedence_rank` identifies authority only when policy or an authorized decision establishes precedence.
- An unresolved material conflict makes the bundle `disputed` and blocks low-risk interpretation or final approval.
- Source locations in findings and criteria use `source_bundle_id`, `source_artifact_id`, and an artifact-local location.
- Any artifact, authority label, ordering, precedence, conflict, or resolution change creates a new bundle version and self-hash.
- Downstream records bind `source_bundle_id`, version, and SHA-256. They may cache artifact details for display but cannot substitute a single artifact hash for the bundle hash.

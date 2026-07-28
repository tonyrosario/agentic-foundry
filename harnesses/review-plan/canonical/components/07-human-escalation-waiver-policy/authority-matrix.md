# Template: human authority matrix

## Purpose

Map logical policy roles to real organizational authority in a versioned, self-hashed deployment record. Keep this configuration separate from prompts so personnel and delegations can change without silently changing reviewer behavior.

The canonical matrix is intentionally unpopulated. Each deployment must fill and activate it with real authority data. Until an active matrix resolves by ID, version, and hash, authority checks deny by default.

## Record

```yaml
schema_version: "1.0"
authority_matrix_id: "authority-matrix-..."
authority_matrix_version: "..."
policy_version: "..."
status: "draft" # draft | active | superseded | revoked
effective_at: null
expires_at_or_event: null
owner: "..."

decision_rules:
  - authority_rule_id: "..."
    decision_class: "..." # specification | evidence | residual-risk | review-waiver | policy-exception | operational | release | cancellation | evaluation-promotion-rollback
    risk_or_domain_triggers: []
    minimum_risk_tier: 0
    maximum_risk_tier: 3
    environments: []
    value_or_blast_radius_limits: []
    required_logical_roles: []
    independent_approval_required: false
    evidence_required: []
    required_conditions: []
    decision_expiry_policy: "..."

authorities:
  - authority_entry_id: "..."
    logical_role: "..."
    person_or_group_identity: "..."
    scope: []
    limits: []
    delegated_by: "..."
    delegation_artifact_sha256: "..."
    effective_at: "..."
    expires_at_or_event: "..."
    backup_or_escalation_identity: "..."

integrity:
  hash_profile: "canonical-json-sha256-v1"
  authority_matrix_sha256: "..."
  supersedes_authority_matrix_id: null
  supersedes_authority_matrix_sha256: null
```

## Rules

- `decision_class` uses the exact shared catalog in the human escalation policy. An unknown or adapter-renamed value is invalid.
- An `emergency-authorization` waiver resolves only through a rule with `decision_class: operational`; that rule's `evidence_required` and `required_conditions` must enforce the emergency hard stop, monitoring and rollback/containment, dual control where feasible, and retrospective.
- Authority is deny-by-default outside an active, unexpired, hash-valid rule and authority entry.
- A title, group membership, or agent-produced role label does not establish authority without the recorded delegation.
- Temporary delegates need explicit effective periods, scope, and limits.
- The person proposing a consequential exception cannot be its sole approver when the matched rule requires separation of duties.
- A matrix change creates a new version and self-hash; never edit an active version in place.
- Superseding or revoking a matrix triggers revalidation of pending and active decisions, waivers, release authorizations, and evaluation promotions bound to it.
- Historical decisions retain the matrix ID/version/hash used at decision time, but consumers must also check whether policy requires reauthorization after supersession.
- Sample or invented authorities are never valid deployment configuration.

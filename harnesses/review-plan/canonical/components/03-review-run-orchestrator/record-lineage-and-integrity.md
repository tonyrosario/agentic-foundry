# Record lineage and referential integrity

## Purpose

Define the hash-bound record chain shared by all eight lifecycle components. Every stage uses these identifiers; adapters may translate transport but cannot change their meaning.

All record and artifact hashes follow the [canonical integrity profile](integrity-profile.md). Unknown profiles or mismatched hashes block progression.

Every edge in the record graph uses the integrity profile’s canonical reference tuple: record type, complete primary/composite identity, schema version, nullable logical record version, self-hash, lifecycle ID where applicable, and role. Bare IDs and parallel ID/hash arrays may be retained only as non-authoritative indexes and can never satisfy a gate.

## Identifier model

| Record | Primary ID | Required parent bindings | Required artifact bindings |
|---|---|---|---|
| Authoritative source bundle | `source_bundle_id` + version | Optional superseding bundle ID/hash | Every source artifact ID/hash, authority, order, precedence, and conflict |
| Lifecycle | `lifecycle_id` | Optional parent lifecycle and exact terminal-state ID/hash; material-feedback successors also bind initiating feedback-event ID/hash | Initial authoritative-source-bundle identity |
| Review input contract | `input_contract_id` | `lifecycle_id`, optional `supersedes_contract_id` | Source bundle, candidate artifact, evidence hashes |
| Classification | `classification_id` | `lifecycle_id`, `input_contract_id` | Source/candidate/surface/evidence hashes, policy version |
| Review manifest | `review_manifest_id` + version | `lifecycle_id`, `input_contract_id`, `classification_id` | Source/candidate/evidence hashes |
| Raw review record | `review_id`, `review_execution_id` | Lifecycle, contract, classification, manifest | Exact reviewed source/plan/evidence hashes |
| Raw finding | `finding_id` | Reserved lifecycle/review/execution identity; the later immutable review record owns the finding through its exact ID/schema/hash | Evidence and plan/source locations |
| Canonical finding ledger | `ledger_id` + version | Lifecycle, contract, classification, manifest, raw reviews/findings | Reviewed source/plan/evidence hashes |
| Human decision | `decision_id` + record version | Lifecycle, contract, finding/policy/gate IDs, authority-matrix ID/version/hash | Exact decision artifacts and authorization-request record hash |
| Waiver | `waiver_id` + record version | Lifecycle, decision, finding/policy/lens IDs, authority-matrix ID/version/hash | Exact source-bundle/plan/repository scope |
| Final closure | `final_closure_record_id` | Lifecycle, contract, classification, manifest, ledger, decisions/waivers | Exact final plan, source, ledger, evidence hashes |
| Conformance review | `conformance_review_id` | Lifecycle, closure, plan-time/diff-time classification | Exact implementation revision and rollout config |
| Release decision/gate | `decision_id` + version, `release_gate_record_id` + version | Lifecycle, conformance, required keyed review executions/waivers, authority matrix, reciprocal ordered record hashes | Exact implementation revision and rollout config |
| Lifecycle state record | `state_record_id`, `transition_number` | Lifecycle, predecessor state ID/hash, typed trigger records, decision/authority hashes when applicable | Active stage contract and artifact hashes |
| Cancellation record | `cancellation_record_id` + version | Lifecycle, exact predecessor state, cancellation decision, authority matrix | Residual-obligation destinations and evidence |
| Feedback event | `feedback_event_id` + version | Lifecycle; exact ID/version/hash references for implicated upstream records; optional ordered acknowledgment of successor-lifecycle genesis and contract | Exact source, plan, implementation, closure, release, decision, waiver, and outcome evidence |
| Learning action | `learning_action_id` | Feedback event IDs | Target component versions and evaluation runs |
| Evaluation run | `evaluation_run_id` | Suite/case and candidate/baseline keyed versions/hashes | Component, prompt, model, adapter, tool-policy hashes; later component-7 authorization binds the completed run hash |

## Cardinality and mapping

- One lifecycle stage binds exactly one authoritative-source-bundle version; that bundle may contain many source artifacts.
- One `lifecycle_id` has one or more immutable stage input contracts linked by `supersedes_contract_id`.
- One input contract may have multiple classification attempts, but exactly one active classification may govern a manifest version.
- One classification produces one or more superseding manifest versions; only one is active for dispatch.
- One manifest assignment has one stable `review_id` and may have multiple execution attempts, each with a unique `review_execution_id`.
- One raw finding belongs to exactly one review execution.
- Findings are sealed before their owning review record; the accepted review record hashes each finding tuple. A finding does not hash the later review record.
- Every raw finding maps to exactly one canonical ledger finding. A ledger finding may map multiple duplicate raw findings.
- One lifecycle may have multiple ledger versions and closure attempts, but only one non-superseded final closure may authorize the exact final-plan hash.
- A conformance review and release decision bind one exact implementation revision and rollout configuration.
- One lifecycle state stream has one genesis record and exactly one accepted successor per predecessor hash; transition numbers are consecutive and the atomic head identifies the only current state.
- One terminal parent/trigger tuple admits at most one successor per authorized reserved lifecycle ID. Nonterminal supersession seals the reserved ID before the parent `superseded` hash exists; successors of an already terminal parent are created only after binding that existing terminal hash.

## Immutable stage contracts

Create a new component-2 input contract for each material lifecycle stage: plan-time classification/review, adjudication, final re-review, diff-time classification/review, conformance, and release. Never mutate a frozen contract.

The new contract:

- keeps the same `lifecycle_id` when pursuing the same authoritative outcome;
- records `supersedes_contract_id` for the previous applicable stage contract;
- pins its own exact artifacts and permissions;
- records the reason and semantic revision summary;
- cannot inherit approval from the superseded contract.

Create a new lifecycle linked by `parent_lifecycle_id` when the authoritative outcome is replaced rather than clarified, when policy treats the work as an independent delivery decision, or when material post-closure feedback requires corrective work. Every terminal successor follows the origin-specific ordered handshake in the lifecycle state machine, begins at `draft`, and receives a fresh input contract and classification.

## Integrity rules

1. A foreign key is valid only when `lifecycle_id` matches and all repeated artifact hashes agree, except an explicitly modeled cross-lifecycle parent/successor binding. Such a binding follows its origin-specific ordered handshake and names every earlier record by exact tuple; no record is required to hash a record that does not yet exist.
2. A mutable path, branch, tag, or filename does not establish artifact identity without a content hash or immutable revision.
3. Records are append-only after their terminal stage status. Corrections create superseding versions that preserve the original.
4. A stale decision, waiver, ledger, or closure record cannot attach to a changed source, plan, policy, implementation, or evidence bundle.
5. Adapters and agents cannot manufacture missing parent IDs. Missing high-impact lineage blocks progression.
6. Raw findings remain unchanged; adjudication and remediation are represented only in ledger versions.
7. Final and release authority is valid only for exact artifact hashes recorded in the decision.
8. Every downstream record retains enough provenance to reconstruct the complete upstream chain without conversational context.
9. State transitions validate the exact predecessor hash, typed trigger hashes, decision/authority hashes, and atomic head; IDs or timestamps alone never establish transition validity.
10. Feedback events resolve every versioned upstream record by exact ID, version where applicable, and self-hash. A later decision or waiver version cannot replace the version that governed the implicated release.
11. A post-closure response cannot mutate or reopen the parent state stream. Its new lifecycle genesis and first contract hash-bind the sealed initiating feedback event and parent terminal state; a later feedback-event version acknowledges the sealed successor records in an ordered, non-circular handshake.
12. Every parent or credited execution resolves through one keyed canonical reference tuple. Gate logic never joins separate ID and hash arrays or resolves a mutable “active/latest” record.
13. For a nonterminal parent, a supersession decision reserves the successor ID before the parent terminal record and the successor genesis is created only after that terminal hash exists. Successors of an already terminal parent bind that exact state plus the origin-specific decision/event/cancellation records.

## Integrity failure response

On missing, conflicting, or stale lineage:

1. Stop the affected transition.
2. Mark the stage `blocked` or `not-established`.
3. Preserve all conflicting record references.
4. Escalate suspected authority or artifact substitution through component 7.
5. Issue corrected/superseding records and re-run every gate whose input changed.

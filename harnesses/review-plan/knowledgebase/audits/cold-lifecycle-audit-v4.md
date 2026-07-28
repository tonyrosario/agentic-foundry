# Cold audit v4: eight-component review lifecycle

- Audit type: cold, independent, read-only
- Reviewer: Terra, medium reasoning
- Date: 2026-07-22
- Scope: only the files directly inside lifecycle component folders `01` through `08`
- Boundary: canonical vendor-neutral specifications/templates; executable runtimes are separate; authority matrix is deployment-populated and deny-by-default

## Verdict

**COHESIVE WITH GAPS**

## Pipeline map

```text
source bundle
      ↓
frozen stage contract
      ↓
classification and manifest
      ↓
immutable review executions and findings
      ↓
adjudicated ledger and remediation
      ↓
exact-hash final closure
      ↓
diff-time classification and conformance
      ↓
hash-bound release authorization
      ↓
observation and feedback
      ↓
evaluated learning change
```

The components consistently preserve lifecycle IDs, source-bundle identity, exact plan and implementation artifacts, raw-versus-adjudicated authority, selected-versus-execution-required lenses, unresolved-review handling, final-plan re-review, and exact-revision release authorization.

## Findings

### Major: lifecycle transition records are not themselves hash-bound to prerequisite or authority records

**Evidence:** `03-review-run-orchestrator/lifecycle-state-machine.md`, “Lifecycle state record,” has only `trigger_record_id` and free-form `authorized_by`; it includes `supersedes_state_record_id` but no prior-state hash, trigger-record hash/type, decision-record hash, or authority-matrix binding. `03-review-run-orchestrator/record-lineage-and-integrity.md`, “Identifier model,” does not define state-record parent or artifact bindings.

**Consequence:** A competent implementation must invent how to prove a transition used the exact valid closure, decision, waiver, conformance, or prior state. Competing records can claim the same predecessor, and a stale or substituted trigger can be referenced by ID alone. This weakens the otherwise strong exact-hash guarantees at the component that advances lifecycle state.

**Smallest correction:** Add to the state record `previous_state_record_sha256`, typed trigger references with IDs, versions, and self-hashes, authority-decision ID/version/hash and authority-matrix ID/version/hash when applicable, and a rule that exactly one valid successor may consume a predecessor state hash.

### Moderate: cancellation obligations and authorization are asserted but have no canonical representation

**Evidence:** `03-review-run-orchestrator/lifecycle-state-machine.md`, “Exception and recovery transitions,” permits `Any nonterminal state → cancelled` with “residual obligations assigned”; “Terminal states” says such obligations “remain linked.” The state record has no cancellation-decision reference, obligation list, owner, due event, or closure evidence.

**Consequence:** A lifecycle can satisfy the written `cancelled` transition while silently losing mandated residual work such as cleanup, customer communication, waiver-expiry handling, or containment because implementers must invent where it is represented and who verifies it.

**Smallest correction:** Define a cancellation decision/obligation record, or add a hash-bound `cancellation` block to the state record containing authority decision, residual-obligation IDs, owners, deadlines/events, and their verification or transfer destination.

### Moderate: lifecycle state validity depends on an underspecified “newest valid record” rule

**Evidence:** `03-review-run-orchestrator/lifecycle-state-machine.md` states, “The current state is the newest valid record in the lifecycle chain,” while the state record only has `entered_at` and an unhashed predecessor ID.

**Consequence:** Concurrent, backdated, or independently appended records have no defined conflict-resolution or linearization behavior. An implementation must invent whether timestamp, storage ordering, signature time, or predecessor topology determines the active state, with potentially different gate outcomes.

**Smallest correction:** Define a single-writer/compare-and-swap requirement or an append-only hash-linked state sequence with a monotonic transition number and conflict rejection.

## Component status

| Component | Status | Assessment |
|---|---|---|
| 1. Common finding schema | Complete | Immutable raw findings/reviews and adjudication boundary are clear. |
| 2. Review input contract | Complete | Source bundles, artifact pinning, authority, projections, and stage contracts are specified. |
| 3. Review-run orchestrator | Partial | Routing, lenses, integrity, and recovery are strong; state-transition record integrity is incomplete. |
| 4. Adjudication/remediation ledger | Complete | Raw-to-ledger mapping, unresolved executions, remediation, and nonblocking progression are enforceable. |
| 5. Final closure gate | Complete | Requirement-versus-residual-risk semantics and exact-final-hash closure are explicit. |
| 6. Evaluation/drift harness | Complete | It tests key lifecycle/integrity bypasses and governs component changes. |
| 7. Human escalation/waiver policy | Complete | Deny-by-default deployment matrix, bounded decisions, waivers, and ordered release handshake are coherent. |
| 8. Post-implementation feedback loop | Complete | Diff-time review, conformance, release gate, observations, and learning feedback are connected. |

## Remaining implementer questions

1. What serialization or concurrency mechanism establishes the one authoritative successor state record for a lifecycle?
2. Which canonical record carries cancellation obligations, and what evidence closes or transfers them?
3. How are state-transition trigger records typed and hash-validated across closure, waiver, decision, conformance, and release-gate variants?
4. What deployment-specific policy populates the intentionally blank authority matrix, including separation-of-duties and reauthorization rules?

## Most consequential issue

The state machine is the sole transition authority, yet its records do not hash-bind the prerequisite and authority records that justify those transitions. Everything else can be exact-hash validated while lifecycle progression itself remains dependent on implementer-invented linkage and ordering.

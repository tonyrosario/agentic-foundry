# Cold audit v7: eight-component review lifecycle

## Execution profile

- Auditor model: `claude-opus-4-8`
- Reasoning effort: `high`
- Context mode: `cold / no conversation history`

> Note on the model field: the report template supplied in the audit request pre-filled
> `Auditor model: gpt-5.6-sol`. That value does not describe the agent that actually ran this
> audit, and the request separately (twice) specifies `claude-opus-4-8` and instructs that these
> values "must reflect the actual model and effort configuration used to launch the audit." The
> accurate value is therefore recorded above. The audit was run by `claude-opus-4-8`.

## Scope and method

### Files permitted and read (canonical component documents + template index)

**01 — common finding schema**
- `01-common-finding-schema/finding-record.md`
- `01-common-finding-schema/review-record.md`

**02 — review input contract**
- `02-review-input-contract/authoritative-source-bundle.md`
- `02-review-input-contract/review-input-contract.md`

**03 — review-run orchestrator**
- `03-review-run-orchestrator/review-suite-selector.md`
- `03-review-run-orchestrator/review-lens-catalog.md`
- `03-review-run-orchestrator/classification-record.md`
- `03-review-run-orchestrator/review-manifest.md`
- `03-review-run-orchestrator/record-lineage-and-integrity.md`
- `03-review-run-orchestrator/integrity-profile.md`
- `03-review-run-orchestrator/lifecycle-state-machine.md`
- `03-review-run-orchestrator/build-review-router-skill-prompt.md`

**04 — adjudication & remediation ledger**
- `04-adjudication-remediation-ledger/finding-adjudicator.md`
- `04-adjudication-remediation-ledger/finding-ledger.md`

**05 — final closure gate**
- `05-final-closure-gate/final-plan-rereview.md`
- `05-final-closure-gate/final-closure-record.md`

**06 — evaluation & drift harness**
- `06-evaluation-drift-harness/evaluation-and-drift-harness.md`
- `06-evaluation-drift-harness/evaluation-case.md`
- `06-evaluation-drift-harness/evaluation-run-record.md`
- `06-evaluation-drift-harness/evaluation-suite-manifest.md`

**07 — human escalation & waiver policy**
- `07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md`
- `07-human-escalation-waiver-policy/authority-matrix.md`
- `07-human-escalation-waiver-policy/escalation-and-decision-record.md`
- `07-human-escalation-waiver-policy/risk-waiver-record.md`
- `07-human-escalation-waiver-policy/cancellation-obligation-record.md`

**08 — post-implementation feedback loop**
- `08-post-implementation-feedback-loop/post-implementation-feedback-loop.md`
- `08-post-implementation-feedback-loop/post-implementation-conformance-review.md`
- `08-post-implementation-feedback-loop/release-gate-record.md`
- `08-post-implementation-feedback-loop/feedback-event-record.md`
- `08-post-implementation-feedback-loop/learning-action-record.md`

**index**
- `README.md`

### Files deliberately excluded (per instruction)

All prior cold-audit and adjudication artifacts were excluded and not opened:
`cold-lifecycle-audit.md`, `cold-lifecycle-audit-v2..v6.md`, every `*-adjudication.md`,
`adversarial-falsification-review.md`, `independent-outcome-audit.md`,
`reviewers-to-build-next.md`, repository history, and anything outside the eight component
folders and the template index. This is a fresh cold read of the current canonical documents.

### Method

Integration audit, not per-file summarization. For each cross-component handoff I resolved the
identifier model in `integrity-profile.md` and `record-lineage-and-integrity.md`, then traced
every required lifecycle path through the state machine, testing the eight handoff questions and
attempting gate-passing counterexamples that violate the intended invariant. I treated
intentionally-blank, deny-by-default deployment configuration (e.g., the unpopulated authority
matrix, blank thresholds) as correct-by-design and did not fault it. I did not require executable
code from a specification knowledgebase.

## Verdict

**COHESIVE WITH GAPS**

One material (moderate) semantic gap was found. No blocker or major defect was found. The eight
components otherwise form one internally consistent, implementable lifecycle: identity, hashing,
lineage, ordering/concurrency, terminal semantics, authority vocabulary, and evaluation coverage
are mutually compatible, and the great majority of the adversarial counterexamples I constructed
are correctly blocked by an explicit written gate.

## Executive assessment

If competent engineers implemented these specifications exactly as written, they would in almost
all respects produce one compatible review lifecycle. The record graph is anchored on a single
canonical reference tuple (`integrity-profile.md` §"Referenced-record validation") that every
component reuses; the "never resolve active/latest/an ID alone" rule is stated once and enforced
consistently downstream; self-hash circularity is avoided everywhere by an explicit ordered
seal-then-acknowledge handshake (findings→review, run→decision, gate→decision→gate,
event→genesis→acknowledgment, reserve-id→terminal→genesis); concurrent progression is serialized
by one atomic state-stream head that binds exactly one version of each governing record as a
trigger; and terminal states are immutable with well-defined, non-circular successor creation for
all three cross-lifecycle origins.

The single material gap is a representational asymmetry at the final-closure layer: closure carries
a full keyed progression-decision tuple (plus a validity flag) for nonblocking *findings*, but only
an ID-only `progression_decision_id` for nonblocking *required-but-inconclusive review executions*.
Because the closure schema itself supplies no keyed tuple for that item type, a still-conforming
implementation can credit `valid-nonblocking-progression` for a `not-established`/`failed` required
review from an unkeyed or stale progression decision at the closure record itself — a local breach
of the system's own "a gate may credit only through a canonical reference tuple" invariant. It is
backstopped (not eliminated) by the ledger the closure binds, and it cannot by itself let a
high-impact inconclusive review escape, because materiality gating independently blocks those.

## Path analysis

Every required lifecycle path was traced. Invariant status below.

1. **Normal approval → release → observation → closure.** Holds.
   `draft→input-frozen→classified→reviews-running→reviews-complete→adjudication-running→
   final-review-ready→final-review-running→plan-approved→implementation-active→diff-classified→
   release-pending→release-authorized→released→observing→closed`. Each transition names a canonical
   prerequisite record and authority; `reviews-complete` explicitly disclaims lens sufficiency;
   closure is version-specific and hash-bound; release authorization is exact-revision. No
   self-certification path exists (state machine "Hard transition rules").

2. **Revision and re-review.** Holds. `adjudication-running→revision-required→input-frozen` with a
   new contract in the same `lifecycle_id`; "A material revision during remediation always returns
   to `input-frozen`; it never jumps directly back to final review." Prior approval never carries
   forward (final-closure-record "Approval is version-specific"; contract lineage rules).

3. **Failed / `not-established` required reviews.** Holds through adjudication and closure.
   review-record retains reason/affected-lens/materiality even with no findings; ledger maps each to
   exactly one `unresolved_review_executions` item defaulting to blocking; closure hard-gates on a
   missing unresolved-review ledger item and on an unresolved item without replacement or valid
   nonblocking progression. **Exception:** the *representation* of the nonblocking-progression credit
   for this item type at the closure layer is under-keyed — see Finding M1.

4. **Review-waiver and residual-risk handling.** Holds. A waived lens stays in `selected_lenses`,
   is removed from `execution_required_lens_ids` only while a valid keyed component-7 waiver +
   authority-matrix binding is present; residual risk requires a scoped component-7 acceptance and
   cannot close a `source-requirement-defect`. Vocabulary is shared (`review-waiver`,
   `residual-risk`). Closure re-verifies waiver validity and preserves waived-lens visibility.

5. **Blocking and re-entry.** Holds. `blocked` is nonterminal, preserves `blocked_from_state`, all
   reasons, and one `resume_target_state`; plan-stage re-entry via `input-frozen`, impl/release-stage
   re-entry via `diff-classified`, each requiring a fresh contract and resolved reasons.

6. **Rollback and recovery.** Holds. `released/observing→rolled-back→implementation-active` binds the
   rolled-back revision, opens component-8 feedback, requires active feedback ownership and a new
   implementation-stage contract before another release attempt. Eval `rollback-reentry` case exists.

7. **Cancellation and residual obligations.** Holds. `cancelled` requires an active component-7
   cancellation record bound to the exact predecessor state + decision + authority; every obligation
   has a durable keyed destination or an evidence-backed, verified no-obligation assertion;
   cancellation cannot waive an obligation; append-only obligation tracking continues post-terminal
   without changing state. `successor-lifecycle` transfer cannot forward-reference a not-yet-created
   post-cancellation successor (avoids the circular-hash trap).

8. **Outcome supersession.** Holds. Reserve-unused-ID → seal parent `superseded` against expected
   head → compare-and-create one genesis under the reserved ID; interrupted creation retries only the
   same reserved ID. Already-`closed` parents use a direct bound genesis without mutation. No
   successor hash is required before the terminal parent hash exists.

9. **Post-cancellation successors.** Holds. Genesis binds the exact cancelled state + current
   cancellation-record version + initiating decision; existence alone inherits/discharges nothing;
   obligation transfer requires a later append-only cancellation version naming the successor +
   evidence.

10. **Material post-closure feedback and successor remediation.** Holds. `closed` never reopens; the
    ordered event(`required-pending`)→genesis+contract→event(`acknowledged`) compare-and-swap admits
    exactly one successor, preserves the initiating event hash, and forces fresh
    classification/contract with no inherited authority. Late feedback resolves every governing
    decision/waiver/closure/conformance/release-gate by exact version+hash and forbids
    latest-version substitution (feedback-event "Lineage rules"; record-lineage rule 10).

11. **Evaluation promotion / shadowing / blocking / rollback.** Holds. Run is self-hashed first;
    a separate component-7 `evaluation-promotion-rollback` decision binds the exact run/suite +
    candidate + authority; registry applies only the hash-bound effect; `NOT ESTABLISHED` is
    fail-closed. Suite activation is a parallel run-then-decision handshake. No circular hash.

12. **Concurrency of non-state records (ledger/manifest/closure versions).** Holds, by construction.
    These version chains do not each carry an independent atomic head, but the single atomic
    state-stream head binds exactly one version of each as a typed trigger, so a forked ledger/
    manifest version that is never bound into the accepted chain is orphaned and cannot govern
    progression. This is sound but implicit; see Remaining implementer questions.

## Findings

### Material findings

#### M1 — moderate — Closure credits nonblocking progression for inconclusive *review executions* through an ID-only reference, unlike for findings

- **Severity:** moderate
- **File/section evidence:**
  - `05-final-closure-gate/final-closure-record.md`, `review_execution_closure[]` (fields:
    `review_id`, `review_execution_id`, `review_record_schema_version`, `review_record_sha256`,
    `unresolved_review_ledger_id`, `replacement_review_ids`, **`progression_decision_id`**,
    `closure_status: established | resolved-by-replacement | valid-nonblocking-progression |
    blocking`). The progression authority is carried as a bare ID; there is **no**
    `progression_decision_record_version` / `_schema_version` / `_sha256` and no
    `progression_record_valid` boolean in this block.
  - Contrast in the same record: `unresolved_items[]` (for *findings*) carries the full keyed tuple
    `progression_decision_id` + `progression_decision_record_version` + `_schema_version` +
    `_sha256` + `progression_owner` + `expires_at_or_event` + `required_rereview_lenses` +
    `progression_record_valid`.
  - Closure "Hard gates": "A required failed or `not-established` review remains unresolved without a
    completed replacement review **or a valid nonblocking progression record**." The finding-side
    gate ("Any unresolved item lacks a valid nonblocking progression record, or its decision, owner,
    expiry, artifact scope, or required re-review is invalid") is written against `unresolved_items`
    (findings), not against `review_execution_closure`.
- **Violated invariant:** `integrity-profile.md` §"Referenced-record validation": "A gate may credit
  or validate a record only through a canonical reference tuple … Reject a parallel ID/hash list …
  Never resolve … a mutable status index … in place of the stored identity tuple." Also
  `record-lineage-and-integrity.md` rule 12 ("Every parent or credited execution resolves through
  one keyed canonical reference tuple") and rule 8 ("Every downstream record retains enough
  provenance to reconstruct the complete upstream chain").
- **Gate-passing counterexample (incompatible conforming outcome):** A Tier-1 lifecycle has one
  required `verification-quality` execution that returns `not-established` at low materiality (a
  legitimately nonblockable class). Implementer A resolves the progression authority strictly: it
  follows `unresolved_review_ledger_id` into the bound ledger's `unresolved_review_executions` item
  and validates the keyed `progression_decision_*` tuple, owner, and expiry there. Implementer B
  reads only the closure record: it sees `closure_status: valid-nonblocking-progression` and a
  present `progression_decision_id`, finds every enumerated closure hard-gate satisfied (an
  unresolved-review ledger item exists; the item is not "blocking"), and approves — even though the
  named progression decision is expired, belongs to a superseded ledger version, or is an ID that
  never resolves to a `evaluation`/`specification`-class component-7 progression decision at all.
  Both implementations conform to the closure schema and its enumerated hard gates; they reach
  opposite approval outcomes on the same inconclusive-review lifecycle. That is precisely an
  "exact conformance still permits materially different behavior" defect.
- **Why existing validation does not prevent it:** The closure's own hard-gate list never demands a
  keyed progression tuple, owner, expiry, or a `progression_record_valid: true` flag for
  `review_execution_closure` entries (it demands them only for `unresolved_items`/findings). The
  deterministic eval check "unresolved-review ledger coverage for every required failed or
  `not-established` execution" validates the *ledger*, not the closure record's progression credit,
  and the closure→ledger cross-check is left to the implementer rather than being an explicit
  closure-local gate. No `required_case_classes` entry pins "closure credits a nonblocking
  progression for an inconclusive required review via an unkeyed/stale progression decision"
  (`inconclusive-review-escape` targets ledger creation; `review-execution-substitution` targets
  crediting an *execution/lens*, not the progression *authority*).
- **Smallest correction:** In `final-closure-record.md`, extend each `review_execution_closure[]`
  entry with `progression_decision_record_version`, `progression_decision_record_schema_version`,
  `progression_decision_record_sha256`, `progression_owner`, `expires_at_or_event`, and
  `progression_record_valid`, mirroring `unresolved_items`; and add one closure hard-gate line: "A
  `review_execution_closure` entry with `closure_status: valid-nonblocking-progression` whose
  progression decision is not a valid, unexpired, keyed component-7 progression tuple bound to this
  ledger is invalid." Optionally add a seeded eval case of the class above.

### No other material findings

No blocker or major material semantic defect was found. The remaining observations are editorial
hardening, not defects that change compatible behavior; they are listed separately below.

## Optional hardening (non-material — do not block implementation)

- **H1 — README stale link.** `README.md` line 3 links maintenance guidance to
  `../06-maintenance-and-evaluation.md`, but the actual component 6 is
  `06-evaluation-drift-harness/`; that target does not correspond to any file in scope. Navigation
  only; no lifecycle semantics depend on it. Fix: point to
  `06-evaluation-drift-harness/evaluation-and-drift-harness.md`.
- **H2 — decision-state wording drift.** `human-escalation-and-waiver-policy.md` §4 lists `expired`
  and `revoked` among "one decision" states, while `escalation-and-decision-record.md`
  `decision.state` enum omits them (they are modeled instead as the record's top-level
  `status: … | expired | revoked` and the `lifecycle.revoked_at`/`revocation_reason` fields). The
  record's model is the more coherent one (expiry/revocation are post-decision lifecycle events).
  No gate reads `decision.state` for validity — closure/waiver validity use boolean flags
  (`not_expired_or_revoked`, "expired … treated as absent") — so behavior does not diverge. Fix:
  align the policy prose to describe `expired`/`revoked` as decision *status/lifecycle* transitions,
  not decision *states*.
- **H3 — decision-class case coverage.** The shared 9-value decision-class vocabulary is enforced by
  deterministic schema validation and by the authority matrix ("unknown or adapter-renamed value is
  invalid"), but the suite's `required_case_classes` has no dedicated case for an adapter renaming a
  canonical decision class. Covered indirectly; a seeded case would make the guarantee first-class.

## Component status

- **01 — common finding schema.** Consistent. One-way findings→review seal avoids circular hashing;
  raw findings immutable; `not established` preserved; every `finding_id` maps to exactly one ledger
  finding. No defect.
- **02 — review input contract.** Consistent. One immutable contract per material stage; origin-kind
  successors bind exact parent terminal state + initiating trigger; `parent_delivery` pins the prior
  release chain; reserved IDs are explicitly non-authoritative. Dispatch-rejection and
  `not established`-capable dispatch rules are complete. No defect.
- **03 — orchestrator (selector, lens catalog, classification, manifest, lineage, integrity profile,
  state machine, router prompt).** Strongest and most load-bearing component; internally consistent.
  Canonical reference tuple, self-hash exclusion set, atomic state-head CAS, single-successor
  cardinality, and origin-specific terminal handoffs are all mutually compatible. `selected` vs
  `execution_required` lens algebra is identical across selector/classification/manifest/router.
  No defect.
- **04 — adjudication & remediation ledger.** Consistent. Sole disposition authority; keyed parent/
  finding/execution tuples; `finding_type` closure semantics; unresolved-review coverage with full
  keyed progression tuple; `ready-for-final-review` preconditions independently re-verified by
  component 5. No defect. (Component 5's *representation* of the ledger's review-execution
  progression is where M1 lives — the ledger side is correctly keyed.)
- **05 — final closure gate.** Consistent except **M1**. Hard gates are otherwise comprehensive:
  exact candidate-hash identity, source-criterion status, source-requirement-defect non-waivability,
  keyed review tuples with result correspondence, waived-lens visibility, material-change
  reclassification. The one asymmetry (keyed progression for findings, ID-only for review
  executions) is the sole material gap in the audit.
- **06 — evaluation & drift harness.** Consistent and unusually complete: its `required_case_classes`
  and zero-tolerance gates enumerate essentially every structural bypass elsewhere in the lifecycle
  (state-stream fork, unkeyed transition/parent/execution, supersession order, orphan release-gate,
  cancellation obligation loss, feedback-version substitution, late-feedback successor loss,
  eval-effect-without-authority). Run-then-decision ordering avoids circular hashes. Gap: no seeded
  case for M1's closure-layer progression credit (folded into the M1 fix).
- **07 — human escalation & waiver policy (policy, authority matrix, decision record, waiver record,
  cancellation record).** Consistent. Shared decision-class catalog is byte-identical across policy,
  matrix, and decision record; deny-by-default authority; release/eval/supersession authorization
  blocks each bind the exact upstream head via ordered handshakes; cancellation obligation and
  post-terminal-correction semantics preserve terminal immutability. Only wording drift H2. No
  material defect.
- **08 — post-implementation feedback loop (loop policy, conformance review, release-gate record,
  feedback event, learning action).** Consistent. Conformance is evidence-not-authorization; release
  gate is append-only CAS with exact-revision binding; feedback lineage forbids latest-version
  substitution; post-closure successor handshake is single-successor and non-circular; learning
  actions must bind the exact eval run + component-7 decision. No material defect.

## Remaining implementer questions

Only questions whose answers would materially change compatible implementation behavior; ordinary
delegated deployment choices (thresholds, personnel, windows, trivial-class policy) are excluded.

1. **M1 resolution.** Until M1 is fixed, must a conforming closure implementation resolve every
   `review_execution_closure` `valid-nonblocking-progression` credit through the bound ledger's
   keyed progression tuple (owner + expiry + validity), and reject a closure that presents only
   `progression_decision_id`? Two conforming implementations diverge on this today; a one-line hard
   gate + schema fields settle it.
2. **Non-state version-fork serialization (informational, not a defect).** Should the record-lineage
   contract state explicitly that ledger/manifest/closure version forks are resolved solely by the
   atomic state-stream head binding one version as a trigger (i.e., these chains intentionally do
   *not* carry their own compare-and-swap head, unlike state/release-gate/cancellation records)?
   Making this reliance explicit would prevent an implementer from inventing a second, conflicting
   "active ledger" resolver.

## Most consequential issue

**M1 (moderate).** At the final-closure gate — the lifecycle's principal approval checkpoint — the
credit that lets a required-but-inconclusive (`not-established`/`failed`) review be treated as
non-blocking is carried by an ID-only `progression_decision_id` in `review_execution_closure`,
without the keyed version/hash/owner/expiry/validity fields that the same record demands for
nonblocking *findings*. Because the closure schema and its enumerated hard gates never require that
keyed tuple for this item type, two engineers implementing the spec exactly as written can reach
opposite approval outcomes on the same inconclusive-required-review lifecycle — one validating the
progression authority through the bound ledger, the other trusting the closure's ID and status
label. This is the only place in the eight components where exact conformance still permits
materially different behavior; every other adversarial path I constructed is caught by an explicit
written gate. The gap is bounded (materiality gating still blocks high-impact inconclusive reviews,
and the bound ledger backstops a strict implementer) and the correction is small (add the keyed
progression fields + one hard-gate line to `final-closure-record.md`, optionally a seeded eval
case), which is why the overall verdict is COHESIVE WITH GAPS rather than NOT COHESIVE.

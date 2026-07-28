# Cold audit v8: eight-component review lifecycle

## Execution profile

- Auditor model: `claude-opus-4-8`
- Reasoning effort: `high`
- Context mode: `cold / no conversation history`

This report was produced by launching a fresh, isolated read of the canonical templates only. No prior audit, adjudication, research note, or conversation state was consulted. The values above reflect the actual model and effort configuration used to run the audit.

## Scope and method

### Files permitted and read

Canonical component documents directly inside the eight component folders, plus the template index:

- `01-common-finding-schema/finding-record.md`, `review-record.md`
- `02-review-input-contract/authoritative-source-bundle.md`, `review-input-contract.md`
- `03-review-run-orchestrator/review-suite-selector.md`, `review-lens-catalog.md`, `classification-record.md`, `review-manifest.md`, `record-lineage-and-integrity.md`, `integrity-profile.md`, `lifecycle-state-machine.md`, `build-review-router-skill-prompt.md`
- `04-adjudication-remediation-ledger/finding-adjudicator.md`, `finding-ledger.md`
- `05-final-closure-gate/final-plan-rereview.md`, `final-closure-record.md`
- `06-evaluation-drift-harness/evaluation-and-drift-harness.md`, `evaluation-suite-manifest.md`, `evaluation-case.md`, `evaluation-run-record.md`
- `07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md`, `authority-matrix.md`, `escalation-and-decision-record.md`, `risk-waiver-record.md`, `cancellation-obligation-record.md`
- `08-post-implementation-feedback-loop/post-implementation-feedback-loop.md`, `post-implementation-conformance-review.md`, `release-gate-record.md`, `feedback-event-record.md`, `learning-action-record.md`
- `README.md`

### Files deliberately excluded

Per instruction, I did **not** read: any `cold-lifecycle-audit*.md` or `*-adjudication.md` in the same directory (v1–v7 audits and every adjudication), `adversarial-falsification-review.md`, `independent-outcome-audit.md`, `reviewers-to-build-next.md`, repository history, or anything outside the eight component folders and the index. This is a fresh closure audit of the current canonical documents as they stand.

### Method

I treated the set as one system. I traced record lineage across all eight components, tested every ordered hash handshake for circularity and races, walked every required lifecycle path against the state machine, and actively constructed counterexamples attempting to make each path pass its written gates while violating its intended invariant. Two mechanical cross-checks were run against the decision-class catalog and the emergency path.

## Verdict

**COHESIVE WITH GAPS**

## Executive assessment

If competent engineers implemented these specifications exactly as written, they would produce one coherent, hash-bound review lifecycle whose normal, revision, failure, waiver, blocking, rollback, cancellation, supersession, and post-closure paths interlock correctly. The integrity model (RFC 8785 canonical-JSON SHA-256, self-hash exclusion, keyed reference tuples, ban on ID-only and parallel-array joins) is applied consistently across every record. The append-only, compare-and-swap lifecycle state stream acts as the single serialization point for all consequential transitions, which cleanly neutralizes the "ambiguous head / fork" class of failure even where subsidiary records (ledgers, closures, gates) could otherwise fork: only the record consumed by the one accepted state transition can advance the lifecycle. Every ordered handshake I examined — finding→review, gate-request→decision→authorized-gate, run→evaluation-decision, initiating-event→successor→acknowledgment, supersession reservation→terminal→genesis, cancellation→post-cancellation-successor — is genuinely non-circular: no record is required to hash a not-yet-created record. Preservation of `failed`/`not-established` reviews is enforced redundantly through the manifest, the ledger's unresolved-review items, and the closure gate. The evaluation suite's required case classes and zero-tolerance gates map one-to-one onto essentially every material bypass in the lifecycle.

The system is **not** perfectly closed. One material coherence gap survives: the emergency-authorization path names a waiver type and is referenced as a required component-7 action, but there is no corresponding member in the closed, exhaustive decision-class catalog, and the catalog cannot be extended without tripping the decision-class-normalization gate. This leaves the authorizing decision's class — and therefore its authority-matrix binding — undefined, permitting materially different conforming implementations of a required governance path. The remaining items are minor or editorial and do not threaten implementability.

## Path analysis

Each required path is stated with the invariant it must preserve and the result of my attempt to break it.

### 1. Normal approval → release → observation → closure
`draft → input-frozen → classified → reviews-running → reviews-complete → adjudication-running → final-review-ready → final-review-running → plan-approved → implementation-active → diff-classified → release-pending → release-authorized → released → observing → closed`.
Invariants hold. Every transition names a canonical trigger record and (where consequential) a decision/authority tuple; CAS on the state head admits one successor. Approval binds the exact final-plan hash (`final_candidate_plan.sha256 == final_review_manifest_candidate_sha256`), release binds the exact implementation revision and rollout-config hash, and `observing → closed` is fail-closed on "no unresolved feedback action." **Holds.**

### 2. Revision and re-review
`adjudication-running → revision-required → input-frozen → …`. A material revision always re-enters at `input-frozen` (state machine "Blocking and re-entry"), forcing new contract/classification/manifest/ledger/closure versions; prior approval never carries forward. **Holds.**

### 3. Failed / `not-established` required reviews
Routed three ways that all key on the execution **result**: manifest `reviews-complete` requires an immutable record and unresolved-review routing; ledger requires a `unresolved_review_executions` item per failed/`not-established` result; closure hard-gates on any such review lacking a canonical unresolved item or a valid nonblocking progression record. Counterexample attempt (mark the portfolio entry `completed` to dodge routing) fails because the ledger and closure gates key on `result`/`execution_result`, not on the portfolio status field. **Holds** (see Finding 3 for the redundant-status seam).

### 4. Review-waiver and residual-risk handling
A waived lens stays in `selected_lenses`, carries an exact component-7 waiver + authority-matrix binding, and is absent from `execution_required_lens_ids` only while the waiver is valid. Closure hard-gates on a selected lens missing from the manifest, a waived lens without a valid waiver, or an unwaived selected lens missing from the execution-required set. Residual risk may remain only under a valid scoped component-7 acceptance; a source-requirement defect can never be closed by waiver/deferral. **Holds.**

### 5. Blocking and re-entry
`blocked` is nonterminal, preserves `blocked_from_state` + reasons + one `resume_target_state`, and re-enters only via a new stage contract with all blocking reasons resolved. Waiver expiry/scope-mismatch before release → `blocked`. Single successor via CAS prevents branch-on-recovery. **Holds.**

### 6. Rollback and recovery
`released|observing → rolled-back → implementation-active`. `rolled-back` requires an executed rollback/containment record bound to the released revision plus an opened feedback event; recovery requires a new implementation-stage contract and active feedback ownership. Containment (not only full rollback) satisfies the entry, so forward-fix is representable. **Holds** (state name conflates rollback and containment — see Finding 4, minor).

### 7. Cancellation and residual obligations
`any nonterminal → cancelled` requires an active cancellation record binding the exact predecessor state, decision, and authority, with every residual obligation assigned to a durable destination (or a verified, evidence-backed no-obligation assertion). Cancellation cannot waive an obligation. Post-terminal correction preserves the terminal state and obligations while opening feedback. Cancellation-record versions use CAS. Counterexample attempt (name the future post-cancellation successor as a transfer destination at activation) is explicitly blocked — the successor's genesis needs the not-yet-created terminal cancellation hash, so transfer occurs only in a later version. **Holds.**

### 8. Outcome supersession
Nonterminal parent: decision reserves one unused successor ID and binds the expected parent head → orchestrator atomically appends `superseded` (sealing the decision + reserved ID) → exactly one genesis is compare-and-created under the reserved ID binding the parent terminal hash. Already-closed parent: a later specification decision directly compare-and-creates the genesis bound to the existing `closed` state. Non-circular; single successor per reserved ID. **Holds.**

### 9. Post-cancellation successors
After `cancelled` exists, a component-7 decision compare-and-creates one successor binding the exact terminal + current cancellation-record version; existence alone inherits/discharges no obligation. **Holds.**

### 10. Material post-closure feedback and successor remediation
Ordered handshake: seal `required-pending` initiating event (null successor) → create successor genesis + first contract binding the sealed event and parent `closed` state → append `acknowledged` event via CAS on the initiating-event head. Only the one acknowledged successor is dispatchable; the successor never references the acknowledgment. Feedback lineage binds the exact governing decision/waiver **versions** that ruled the implicated release, with later versions marked comparison-only. `closed` never reopens. **Holds.**

### 11. Evaluation promotion / shadow / block / rollback
Run (or candidate suite) is self-hashed first → component-7 `evaluation-promotion-rollback` decision binds the exact run/suite ID+hash, candidate component/version, and effect → registry applies only that hash-bound decision. `NOT ESTABLISHED` is fail-closed absence of effect. Zero-tolerance gate blocks any registry effect without the completed run hash and valid component-7 tuple. **Holds.**

### 12. Independent-lifecycle genesis (cross-cutting)
For terminal successors the genesis-vs-first-contract ordering is fully specified. For an **independent** genesis the templates imply — but do not state outright — that the `draft` record already binds a frozen input contract (its `active_input_contract_id`/`sha256` are shown as populated). The intended pattern is recoverable from the terminal-feedback handshake by analogy, so it holds in practice, but the wording leaves a compatibility seam (see Finding 2, minor).

## Findings

### Finding 1 — Emergency authorization has no canonical decision class (MODERATE, material)

- **Severity:** moderate
- **Evidence:**
  - `07-human-escalation-waiver-policy/risk-waiver-record.md:10` — `waiver_type: "..." # residual-risk | review | policy-exception | emergency-authorization`, plus the dedicated `emergency:` block at `:145`.
  - `07-human-escalation-waiver-policy/human-escalation-and-waiver-policy.md:85–97` — the shared decision-class catalog has exactly nine members: `specification, evidence, residual-risk, review-waiver, policy-exception, operational, release, cancellation, evaluation-promotion-rollback`. Line 99: "Adapters may display friendlier labels but cannot add, omit, or rename decision classes inside canonical records." The Escalation-classes table (`:71–82`) likewise has no emergency row.
  - `07-.../authority-matrix.md:23` and `07-.../escalation-and-decision-record.md:16` — both enumerate the identical nine-member enum for `decision_class` / `trigger.class`.
  - `07-.../risk-waiver-record.md:31–38` — every waiver (emergency included) **requires** a `human-decision` parent tuple (role `waiver-authorization`).
  - `03-review-run-orchestrator/lifecycle-state-machine.md:196` and `08-.../post-implementation-feedback-loop.md:137` — post-closure emergency containment "requires component-7 emergency authorization," i.e., emergency authorization is a required governance path, not optional decoration.
  - `06-evaluation-drift-harness/evaluation-suite-manifest.md:129` / `evaluation-and-drift-harness.md:285` — the `decision-class-normalization-attack` / `accepted-adapter-renamed-or-unknown-decision-class` gate rejects "renamed, aliased, omitted, or **unknown**" decision-class values.
- **Violated invariant:** "Every decision and waiver binds the exact active authority-matrix ID, version, and self-hash plus matched rule and authority-entry IDs" (policy `:116`), combined with "authority is deny-by-default outside an active… rule" (authority-matrix `:56`). Every authorized action must resolve to an authority-matrix rule whose `decision_class` is a catalog member.
- **Gate-passing counterexample / incompatible conforming outcome:** An emergency-authorization waiver (`waiver_type: emergency-authorization`) needs an authorizing `human-decision`. That decision's `trigger.class` must be a catalog member, and it must match an authority-matrix rule of the same class. None of the nine classes is designated for emergencies, and the catalog is closed. A strict deployment therefore has two mutually exclusive conforming choices, both defensible and neither specified: (a) authorize emergencies under `operational` ("break-glass action" is listed there, policy `:78`); (b) under `policy-exception`; or, reading the closed catalog literally, (c) conclude no valid class exists and be unable to authorize an emergency at all. Two conforming deployments authorizing the *same* emergency action under different decision classes bind *different* authority-matrix rules — materially different governance of the same required path — and neither can add an `emergency-authorization` class without the normalization gate rejecting it as an unknown value.
- **Why existing validation does not prevent it:** The normalization gate enforces that the nine classes are never renamed/added, which actively *forbids* the natural fix (adding the class) while the waiver schema keeps `emergency-authorization` as a first-class waiver type. No gate requires the emergency waiver_type to map to a specific decision class, so the mismatch is invisible to every deterministic check.
- **Smallest correction:** State explicitly in the human-escalation policy (and the waiver record) which existing catalog class carries emergency authorization — recommended `operational`, given its break-glass scope — and attach the emergency requirements (hard stop, dual control, retrospective) as required conditions of that class's rule; **or**, if emergency is truly distinct, add `emergency-authorization` to the shared catalog and to all four consumers (policy list, authority-matrix enum, escalation-record enum, state-machine trigger enum) plus the normalization gate's allow-set. One sentence of mapping closes it.

### Finding 2 — Independent-lifecycle `draft` genesis: input-contract binding under-specified (MINOR)

- **Severity:** minor
- **Evidence:** `03-.../lifecycle-state-machine.md:72–74` shows `active_input_contract_id` / `active_input_contract_sha256` as populated string fields on every state record, including genesis. The normal transition `draft → input-frozen` (`:120`) treats the contract as validated only *at* `input-frozen`. The terminal-feedback path (`:191–193`) explicitly creates the genesis `draft` and first contract together, but no equivalent statement exists for an independent genesis.
- **Violated invariant:** none is actually breached; this is an ordering ambiguity, not a contradiction. A record is valid only through keyed tuples, and `input-frozen` re-validates independently, so no integrity failure can result.
- **Gate-passing counterexample / incompatible conforming outcome:** Deployment X mints the `lifecycle_id`, freezes the contract, then creates the genesis `draft` already binding the contract's ID/hash (input-frozen = "validated"). Deployment Y creates the genesis `draft` with placeholder/empty contract fields and only binds the contract at `input-frozen`. Both read as conforming; their genesis records differ in whether `active_input_contract_*` is populated, which matters for cross-adapter record exchange and for evaluation fixtures that assert on genesis contents.
- **Why existing validation does not prevent it:** The state-record schema does not mark `active_input_contract_*` nullable-at-draft, and no gate asserts genesis contract binding for independent lifecycles.
- **Smallest correction:** Add one line to "State-stream ordering and concurrency" stating that for an independent lifecycle the frozen input contract is created before the genesis `draft` and is bound in `active_input_contract_*` at `draft` (mirroring the terminal-feedback rule), or explicitly permit these two fields to be null until `input-frozen`.

### Finding 3 — Review record `status` vs `completion.result` keying seam (MINOR)

- **Severity:** minor
- **Evidence:** `01-common-finding-schema/review-record.md:20` — record-level `status: completed | failed | not-established | superseded`; `:88` — `completion.result: established | not-established | failed`. Downstream routing (`04-.../finding-ledger.md:170`, closure `05-.../final-closure-record.md:144`) keys on `result`/`execution_result`; the manifest `reviews-complete` prose (`03-.../review-manifest.md:154`) speaks of "completed, failed, or explicitly not-established" without naming which field is authoritative.
- **Violated invariant:** intended one-to-one correspondence between an execution's completion result and its routing category.
- **Gate-passing counterexample / incompatible conforming outcome:** An honest not-established execution could carry `status: completed` with `completion.result: not-established`. A validator keying on `status` would treat it as an ordinary completion; only because the ledger and closure gates independently key on `result` does the escape get caught. The design is safe (defense-in-depth), but the redundant `status` field invites divergent validators across implementations.
- **Why existing validation does not prevent it:** No sentence declares `completion.result` the authoritative routing key or requires `status` to be derived from it.
- **Smallest correction:** Add one rule to the review record: "`completion.result` is authoritative for downstream routing; record `status` must not contradict it."

### Finding 4 — `rolled-back` state name conflates rollback and containment (MINOR, editorial)

- **Severity:** minor (editorial)
- **Evidence:** `03-.../lifecycle-state-machine.md:154` — the `released|observing → rolled-back` row accepts an "Executed rollback/**containment** record," and `:206` reuses the same state for recovery. A forward-fix with containment (no full rollback) must pass through a state literally named `rolled-back`.
- **Impact:** No integrity effect; purely a naming/readability issue that can mislead operators and fixture authors into thinking a full rollback occurred.
- **Smallest correction:** Rename to `rolled-back-or-contained`, or add a one-line note that the state covers containment as well as full rollback.

### Finding 5 — `learning-action` field named `release_decision_*` actually binds an evaluation decision (MINOR, editorial)

- **Severity:** minor (editorial)
- **Evidence:** `08-.../learning-action-record.md:46–53` names the component-7 evaluation-promotion decision fields `release_decision_id` / `release_decision_record_*`; acceptance rule `:87` correctly requires them to resolve the "component-7 evaluation decision." The bound value is an `evaluation-promotion-rollback` decision, not a `release` decision.
- **Impact:** Misleading field name; the binding itself is correct. Could cause an implementer to cross-wire release vs evaluation decisions.
- **Smallest correction:** Rename to `evaluation_decision_*`.

### No other material findings

I specifically tried and failed to produce gate-passing counterexamples for: circular self-hashes (all handshakes ordered), ID-only / parallel-array / stale-version / wrong-retry substitution (uniformly rejected by the keyed-tuple rule and integrity profile), orphan records (unreferenced findings/reservations are inert, never integrity-breaking), ambiguous heads (the CAS state stream serializes all consequential transitions), terminal reopening (no outgoing transitions; post-terminal correction preserves state), multi-source-bundle collapse (bundle hash preserved and gated downstream), late-feedback version substitution (governing-version binding enforced), and evaluation effect without authority (fail-closed). These are genuinely closed.

## Component status

- **01 Common finding schema — Cohesive.** Findings sealed before the review record; one-way ownership avoids circular hashing; raw findings immutable, disposition delegated to component 4. Attribution requires the review-owned hash tuple, defeating ID-only credit.
- **02 Review input contract — Cohesive.** Per-stage immutable contracts, `supersedes_contract_id` lineage, bundle/plan/repo pinning, staged role projections, reserved (non-authoritative) downstream IDs, and origin-specific successor bindings all consistent. No inherited approval.
- **03 Review-run orchestrator — Cohesive.** Lens catalog is a closed keyed vocabulary with ingestion-only alias normalization; selector adds-only; classification/manifest precedence (deterministic ≥ semantic, human add-only, waiver preserves selected lens) is uniform; integrity profile and lineage contract are the backbone every other component obeys; the state machine's CAS head is the system's serialization guarantee. The build prompt is explicitly illustrative ("similar to") and scoped to the classifier, so its narrower manifest is not a contradiction.
- **04 Adjudication & remediation ledger — Cohesive.** Sole disposition authority; every raw finding and every failed/`not-established` execution maps to exactly one ledger item; type-specific closure rules (source-requirement defect non-waivable) propagate cleanly into closure. Keyed tuples throughout.
- **05 Final closure gate — Cohesive.** Version-specific approval bound to the exact candidate hash; comprehensive hard-gate list covers lens visibility, unresolved-review coverage, progression-decision validity, and material-change re-routing. State stream consumes exactly one closure to reach `plan-approved`.
- **06 Evaluation & drift harness — Cohesive.** Required case classes and zero-tolerance gates map onto essentially every lifecycle bypass; run-then-decision handoff is non-circular; deny-by-default `NOT ESTABLISHED`; sealed-oracle partitioning and separation-of-duties specified.
- **07 Human escalation & waiver policy — Cohesive with one moderate gap (Finding 1).** Decision classes, roles, authority matrix (deny-by-default, intentionally blank), cancellation obligations, and reciprocal release/evaluation handshakes are otherwise fully consistent. The emergency-authorization class omission is the sole material defect in the whole set.
- **08 Post-implementation feedback loop — Cohesive.** Conformance → release gate → observation → feedback → learning → evaluation chain is hash-bound end to end; governing-version lineage and the one-successor post-closure handshake are airtight; the `release_decision_*` misnaming (Finding 5) is cosmetic.

## Remaining implementer questions

Only questions whose answers would change compatible implementation behavior; ordinary deployment configuration (authority-matrix population, thresholds, windows, trial counts) is excluded because the design intentionally delegates it deny-by-default.

1. **Which of the nine canonical decision classes authorizes an `emergency-authorization` waiver, given the catalog is closed and the normalization gate forbids adding one?** (Finding 1.) The answer fixes the authority-matrix rule and thus the governance of every emergency/break-glass action; different answers yield incompatible conforming deployments.
2. **For an independent lifecycle, must the genesis `draft` state record already bind a frozen input contract (non-null `active_input_contract_id`/`sha256`), or may those fields be null until `input-frozen`?** (Finding 2.) The answer determines cross-implementation genesis-record compatibility and evaluation-fixture assertions.
3. **Which field — record `status` or `completion.result` — is authoritative when routing a review execution to unresolved-review handling?** (Finding 3.) Declaring one settles validator behavior across adapters.

## Most consequential issue

**Finding 1 — the missing `emergency-authorization` decision class.** It is the only defect that (a) is material rather than editorial, (b) touches a path the state machine and feedback loop mark as *required* (post-closure emergency containment), and (c) is made non-trivial by the system's own closed-catalog invariant: the obvious remedy (add the class) is actively forbidden by the decision-class-normalization gate, so a deployment must instead choose an existing class the spec never designates. Two otherwise-perfectly-conforming deployments can therefore govern the same emergency action under different authority rules. Every other observation is a minor or editorial hardening item; the core eight-component lifecycle is internally consistent and implementable as written.

# Template: review-suite selector

## Role

Classify the plan’s risk and choose the smallest review portfolio that covers its material failure modes. Do not perform the reviews.

## Inputs

- Valid review input contract ID: `[review-input-...]`
- Exact source contract: `[path/version/hash]`
- Exact candidate plan or implementation diff: `[path/version/hash]`
- Declared and observed change surfaces: `[manifest/version/hash]`
- System/risk policy: `[path/version/hash]`

## Risk questions

Identify whether the plan changes:

- authentication, authorization, secrets, or trust boundaries;
- personal/sensitive data, retention, legal or policy obligations;
- money, billing, entitlements, or irreversible user effects;
- database/schema/state migrations or backfills;
- public/cross-team APIs, queues, protocols, or compatibility;
- distributed ordering, concurrency, retries, or idempotency;
- deployment topology, infrastructure, capacity, SLOs, or cost;
- external platforms/dependencies with unverified behavior;
- broad customer impact or weak rollback;
- agent tool permissions, credentials, network, or instruction boundaries.

Also score:

- consequence: low / medium / high / critical;
- reversibility: easy / bounded / difficult / irreversible;
- novelty: known pattern / adapted / new;
- coupling: local / one boundary / multi-system / organizational;
- evidence quality: executable / cited / inferred / missing.

## Output

Produce a machine-readable [canonical classification record](classification-record.md) and [canonical review manifest](review-manifest.md), plus a human-readable explanation containing:

1. Lifecycle, input-contract, classification, and review-manifest IDs.
2. Risk tier 0–3 with rationale.
3. Required reviews selected from:
   - `independent-outcome`;
   - `grounded-feasibility`;
   - `requirements-traceability`;
   - `adversarial-falsification`;
   - `verification-quality`;
   - `security`;
   - `privacy-legal`;
   - `data-migration`;
   - `interface-compatibility`;
   - `sequencing-reversibility`;
   - `operational-readiness`;
   - `performance-cost`;
   - `accessibility-product-policy`;
   - `prototype-rehearsal`;
   - `final-plan-rereview`;
   - `implementation-conformance`.
4. Inputs/evidence and component-2 projection each selected reviewer receives.
5. Stable `review_id` assignments and required isolation/capability.
6. Reviews explicitly not selected and why.
7. Human decisions, waivers, and approval roles required.
8. Re-review triggers and blocking unknowns.

Optimize for coverage, not reviewer count.

The selector does not dispatch reviews or alter lifecycle state. Lens IDs must conform to [the canonical lens catalog](review-lens-catalog.md). The orchestrator validates this manifest against [the lineage contract](record-lineage-and-integrity.md) and [lifecycle state machine](lifecycle-state-machine.md).

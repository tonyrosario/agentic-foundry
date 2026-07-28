# Adjudication of cold lifecycle audit v8

- Audit reviewed: [cold lifecycle audit v8](cold-lifecycle-audit-v8.md)
- Auditor execution profile: `claude-opus-4-8`, high reasoning, cold/no conversation history
- Adjudicator: primary implementation agent
- Date: 2026-07-22
- Scope: one moderate finding and four minor findings

## Verdict

All five findings were **valid** and have been corrected.

This is an adjudication and repair record, not another independent audit.

## M1 — Emergency-authorization decision-class mapping

Confirmed. `emergency-authorization` existed as a waiver type and required governance path, but no rule selected one of the nine closed canonical decision classes for its authorizing decision and authority-matrix lookup.

The canonical mapping is now explicit:

- `emergency-authorization` remains a waiver type, not a new decision class;
- its authorizing human decision MUST use `trigger.class: operational`;
- its matched authority-matrix rule MUST use `decision_class: operational`;
- the rule and waiver must enforce a hard stop, monitoring and rollback/containment, dual control where feasible, and retrospective review;
- a `policy-exception` decision, adapter alias, or other class cannot substitute.

The policy, waiver record, authority matrix, decision record, evaluation harness, and evaluation-suite manifest now agree on this mapping. A dedicated case class, deterministic check, and zero-tolerance gate reject missing or incompatible mappings.

## m2 — Independent-lifecycle genesis ordering

Confirmed. The state schema populated `active_input_contract_id` and its hash at genesis, but the independent-lifecycle creation order was implicit.

The input-contract and state-machine specifications now require this sequence:

1. Reserve an unused lifecycle ID.
2. Freeze the first component-2 input contract under that ID.
3. Compare-and-create the genesis `draft` bound to that exact contract ID/hash.
4. Revalidate the existing contract at `draft → input-frozen`.

Null, placeholder, or mismatched genesis bindings are invalid. Component 6 now contains a dedicated case class, deterministic check, and zero-tolerance gate for this rule.

## m3 — Review status/result correspondence

Confirmed. The record-level `status` and `completion.result` fields had overlapping vocabularies without a normative mapping.

`completion.result` is now the authoritative downstream routing key. Current records must use the exact status/result correspondence specified in the review-record integrity rules. Superseded records retain their historical result but cannot satisfy a current execution requirement. Component 6 now tests and gates this correspondence.

## m4 — Containment represented by `rolled-back`

Confirmed as an editorial ambiguity. The state name is retained for compatibility, but the state machine now states that `rolled-back` is the canonical post-release recovery state for either full rollback or bounded containment. The linked execution and feedback records identify what actually occurred; the name does not assert restoration of the original revision.

## m5 — Learning-action evaluation-decision field names

Confirmed. The learning-action record's component-7 evaluation decision fields were misleadingly named `release_decision_*`.

They are now named `evaluation_decision_*`, with `evaluation_recommendation` for the harness recommendation. The existing acceptance rule continues to require the exact component-7 evaluation decision and authority-matrix tuples.

## Verification

- YAML syntax and duplicate-key checks passed.
- The shared nine-value decision-class catalog remains unchanged.
- Emergency waiver, decision, authority, and evaluation rules use the canonical `operational` mapping.
- Independent genesis creation binds the exact first frozen contract before `input-frozen`.
- Review status/result mapping is explicit and evaluation-gated.
- No obsolete `release_decision*` field remains in the learning-action record.
- Markdown headings, fences, local links, and whitespace checks passed.

## Result

All five v8 findings are corrected. No subsequent cold audit was run as part of this work.

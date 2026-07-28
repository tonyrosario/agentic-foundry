From this research, would there be a 'classifer' part of the workflow that said... I see this plan and I recommend the following reviews?  So for plan A that is simple, it could be one reviewer but for plan
  B that touches the database, would need two reviewers (code + database).  and so on


• Yes. That should be an explicit first stage: a review-suite classifier/router.

  I’d have it recommend review lenses rather than merely a reviewer count. The count then falls out naturally.

  A useful flow is:

  ticket + plan + change manifest
                ↓
         review classifier
                ↓
   risk tier + required lenses + evidence + human gates
                ↓
           selected reviews
                ↓
            adjudication

  For example:

   Plan characteristics                         Recommended reviews
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Small, local, reversible change              One combined outcome/feasibility reviewer
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Normal multi-file feature                    Outcome audit + grounded code/test review
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Database schema or migration                 Outcome audit + data/migration specialist
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Database migration with phased deployment    Outcome + data/migration + sequencing/operations
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Authentication or authorization              Outcome + security specialist
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Public API or shared contract                Outcome + compatibility/interface specialist
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Infrastructure, deployment, or SLO change    Outcome + SRE/operational-readiness specialist
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Payments or sensitive data                   Outcome + security/privacy + domain specialist
  ───────────────────────────────────────────  ─────────────────────────────────────────────────────────────
   Several high-risk surfaces                   All triggered lenses, followed by strong human adjudication

  The classifier already exists as a starting template: knowledgebase/templates/03-review-run-orchestrator/review-suite-selector.md.

  The important design choices are:

  - Keep a minimum review floor. Every material plan gets at least an outcome review.
  - Route by risk surface, not plan length. A five-line authorization change may deserve more review than a long internal refactor.
  - Use deterministic triggers plus semantic classification. For example, changes under migrations/, auth modules, infrastructure files, public schemas, or permission policies should mechanically activate the
    corresponding lens. An agent then catches semantic risks not visible from paths.

  - Make the classifier explain every selection and omission.
  - Let it return “cannot classify safely” and escalate.
  - Do not let the classifier waive mandatory organizational policies.
  - Record which lenses were activated so escaped defects can later reveal classifier mistakes.

  A classifier result could look like:

  risk_tier: 2
  reasons:
    - adds a database table
    - changes an existing uniqueness constraint
    - requires production backfill
    - old and new application versions may overlap

  required_reviews:
    - lens: independent-outcome
      reason: baseline review for every material plan

    - lens: data-migration
      reason: schema evolution, backfill, reconciliation, rollback

    - lens: sequencing-operability
      reason: mixed-version deployment and production backfill

  not_required:
    - lens: security
      reason: no new trust boundary or sensitive-data handling identified

  human_gates:
    - database owner approves rollback limitations

  required_evidence:
    - compatibility matrix
    - backfill rehearsal
    - reconciliation query
    - rollback or forward-recovery procedure

  rereview_triggers:
    - schema changes
    - deployment-order changes
    - rollback strategy changes

  For your Plan A versus Plan B example:

  - Plan A: one reviewer can combine outcome, feasibility, and testability if it is genuinely local and reversible.
  - Plan B: at least the baseline outcome reviewer plus a database specialist.
  - If Plan B includes a live migration, backfill, dual-read/write period, or deployment ordering, it should usually add a third operations/sequencing lens.

  The classifier itself should be evaluated like the reviewers. Track both:

  - Under-routing: it failed to request a review that later would have caught a defect.
  - Over-routing: it requested specialists who produced no unique useful signal.

  That gives you a way to tune the routing rules instead of permanently increasing reviewer count after every incident.



would the classifier be better as a skill or agent (or something else)?


• Best as a hybrid:

  - A deterministic policy file for mandatory routing.
  - A skill as the workflow entry point and orchestrator.
  - A cold, read-only agent only for semantic risk discovery.

  Not a standalone agent alone—the classifier is too important to leave entirely nondeterministic.

  /classify-plan skill
          ↓
  deterministic rules ── mandatory lenses
          +
  cold classifier agent ── additional semantic lenses
          ↓
  review manifest

  ## Why this split works

  ### Deterministic policy

  Use policy-as-code for obvious, non-negotiable triggers:

  rules:
    - when:
        paths:
          - "supabase/migrations/**"
          - "db/migrations/**"
      require:
        - data-migration
        - sequencing-reversibility

    - when:
        paths:
          - "auth/**"
          - "middleware/**"
        concepts:
          - authorization
          - session
          - permissions
      require:
        - security

    - when:
        concepts:
          - public API
          - breaking change
          - webhook
      require:
        - interface-compatibility

  Advantages:

  - Predictable
  - Auditable
  - Cheap
  - Testable
  - Cannot silently forget mandatory policy
  - Easy to explain after an incident

  Its weakness is that it catches only known, encoded signals.

  ### Classifier skill

  The skill should own the complete workflow:

  1. Read the ticket and plan.
  2. Produce or validate a change manifest.
  3. Apply deterministic policy.
  4. Decide whether semantic classification is needed.
  5. Invoke the read-only classifier agent.
  6. Merge the results.
  7. Produce the review manifest.
  8. Dispatch reviews if requested.

  A skill is appropriate because this is a reusable organizational procedure, not merely a persona.

  The skill should contain:

  - Input requirements
  - Risk tiers
  - Policy location
  - Classifier prompt
  - Merge precedence
  - Output schema
  - Escalation rules
  - Evaluation commands
  - Review-dispatch instructions

  ### Cold classifier agent

  The agent finds risks that path and keyword rules miss:

  - A UI change actually alters authorization semantics.
  - A “config change” changes production availability.
  - An application change requires a data backfill not mentioned in the plan.
  - A local API change affects another service.
  - A feature flag changes privacy or operator behavior.
  - A new retry loop creates idempotency requirements.

  It should:

  - Be read-only.
  - Start with fresh context.
  - See the ticket, plan, policy, and relevant repository evidence.
  - Recommend additions to the deterministic review suite.
  - Be unable to remove mandatory reviews.
  - Return not established when it lacks evidence.

  ## Merge rule

  Use the union of mandatory and semantic results:

  final reviews =
      baseline reviews
    ∪ deterministic policy reviews
    ∪ semantic classifier additions
    ∪ human-required additions

  The agent must never be able to say, “The migration looks simple, so skip database review,” when policy requires it.

  Removing a mandatory review should require a human waiver with a recorded reason and expiration.

  ## Two classification points

  Run classification twice.

  ### Before implementation

  Classify the proposed plan using:

  - Ticket/spec
  - Plan
  - Declared affected systems
  - Proposed files
  - Data/interface/deployment changes

  This selects plan reviewers.

  ### After implementation

  Reclassify using the actual diff:

  - Changed files
  - Migrations
  - Dependencies
  - Permissions
  - APIs and schemas
  - Infrastructure
  - Test and deployment changes

  This catches plan drift. For example, a plan classified as a normal UI feature might produce an implementation that unexpectedly changes middleware or database constraints.

  ## When the semantic agent can be skipped

  For clearly low-risk work, deterministic classification may be sufficient:

  - Documentation only
  - Test-only changes
  - Formatting
  - Local rename
  - Reversible internal refactor with no boundary changes

  For medium or high-risk plans, run the semantic classifier.

  ## Recommended implementation

  I would package it as:

  review-router/
  ├── SKILL.md
  ├── policy/
  │   ├── baseline.yaml
  │   ├── paths.yaml
  │   ├── concepts.yaml
  │   └── risk-tiers.yaml
  ├── agents/
  │   └── semantic-classifier.md
  ├── templates/
  │   └── review-manifest.md
  ├── evals/
  │   ├── expected-routing.yaml
  │   └── cases/
  └── scripts/
      ├── collect-change-signals
      ├── apply-policy
      └── validate-manifest

  So the short answer is: expose it as a skill, enforce known routing through deterministic policy, and let the skill invoke a cold classifier agent for judgment-heavy additions. This gives you reuse,
  isolation, auditability, and predictable mandatory coverage.



 is there anything else in the review lifecycle that we need to build out?


• Yes. The classifier and reviewers cover selection and critique, but the lifecycle still needs a closed-loop control system. The most important remaining work is not more reviewer types.

  ## Essential components

  1. Review input contract

  Define the minimum artifact package every review receives:

  - Originating ticket or requirement
  - Candidate plan
  - Explicit constraints and non-goals
  - Change/risk manifest
  - Repository access policy
  - Known uncertainties
  - Previous-plan diff for re-reviews

  This prevents review quality from depending on whatever context happened to be supplied.

  2. Common finding schema

  Every reviewer should emit the same structured fields:

  - Finding ID
  - Claim
  - Severity and confidence
  - Requirement affected
  - Exact plan evidence
  - External/repository evidence
  - Concrete failure scenario
  - Required resolution
  - Re-review trigger

  Without this, adjudication becomes subjective transcript interpretation.

  3. Review-run orchestrator

  The classifier selects reviews, but something must execute the manifest reliably:

  - Create isolated reviewer contexts
  - Apply the correct permissions and evidence access
  - Prevent findings from leaking between reviewers
  - Capture prompt, skill, model, and artifact versions
  - Validate reviewer output
  - Dispatch adjudication after parallel reviews finish

  This is primarily deterministic workflow code, with agents performing the judgment steps.

  4. Remediation ledger

  Adjudication should produce a durable record linking every accepted finding to its resolution:

   Finding    Disposition    Plan change    Evidence    Owner    Re-review
  ━━━━━━━━━  ━━━━━━━━━━━━━  ━━━━━━━━━━━━━  ━━━━━━━━━━  ━━━━━━━  ━━━━━━━━━━━

  Allowed dispositions should be constrained: accepted, rejected with evidence, explicitly deferred, waived by an authorized human, or unresolved.

  5. Revision and closure gate

  After the plan is revised:

  - Diff old and new plans.
  - Verify accepted findings were addressed.
  - Re-run the classifier on the diff.
  - Re-run the outcome audit.
  - Re-run affected specialist reviews.
  - Detect new risks introduced by remediation.
  - Issue a final closure verdict.

  This is essential. Otherwise, the lifecycle verifies the obsolete draft rather than the plan that will be implemented.

  6. Evaluation and drift harness

  Treat classifier and reviewer prompts like production code:

  - Gold plans with known defects
  - Clean plans where “no finding” is correct
  - Seeded-defect tests
  - Routing tests for deterministic triggers
  - Adapter-equivalence tests for Claude and Codex
  - False-positive, false-negative, and unsupported-finding rates
  - Reviewer overlap and unique-findings metrics
  - Regression tests when prompts, models, or policies change

  Run these before publishing changes and periodically against holdout cases.

  7. Human escalation and waiver policy

  Define where automation loses authority:

  - Unresolved source ambiguity
  - Conflicting requirements
  - Irreversible migrations
  - Security acceptance
  - Compliance or privacy exposure
  - Large blast radius
  - A reviewer/adjudicator disagreement that evidence cannot resolve

  Agents may recommend a waiver; an authorized human should own consequential risk acceptance.

  8. Post-implementation feedback loop

  Compare reviews with what actually happened:

  - Implementation defects
  - PR-review findings
  - Test escapes
  - Rollbacks and incidents
  - Scope changes discovered during implementation
  - Reviewer findings later shown to be false

  This is how you discover blind spots and decide whether another specialist reviewer is genuinely warranted.

  ## Recommended build order

  1. Common finding schema
  2. Review input contract
  3. Orchestrator and provenance recording
  4. Adjudication/remediation ledger
  5. Diff-aware final closure gate
  6. Evaluation and drift harness
  7. Human waiver policy
  8. Post-implementation feedback loop

  The largest remaining gap is the final closure gate. Without it, the system can classify and review a draft correctly, revise that draft, and then approve a final plan whose material changes were never
  independently evaluated.

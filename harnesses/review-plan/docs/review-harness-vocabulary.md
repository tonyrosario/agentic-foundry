# Review harness vocabulary and composition

`review-plan` is a **review harness**: a small system combining specifications, skills, agent executions, deterministic software, policies, records, and evaluations.

It is not one skill or one agent.

## Vocabulary

| Term | Meaning |
|---|---|
| **Harness** | The complete environment that makes model work repeatable and governable: instructions, tools, models, workflow, state, validation, permissions, and evaluation. |
| **Component** | One logical responsibility in the canonical design. A component may require several files or runtime elements. |
| **Prompt** | Instruction text given to a model for one task. It is the smallest and least structured unit. |
| **Skill** | A reusable package for a bounded capability. It may contain prompts, instructions, schemas, reference material, and scripts. A skill does not execute itself. |
| **Agent** | A running model instance given a role, context, permissions, tools, and usually a skill. Agents are executions, not permanent artifacts. |
| **Role** | The responsibility assigned to an agent, such as reviewer, adjudicator, or reviser. |
| **Review lens** | The specific question a reviewer examines, such as outcome coverage, database safety, security, or testability. |
| **Tool** | A callable capability available to an agent, such as repository search, tests, filesystem access, or an external API. |
| **Model profile** | A configured model, reasoning effort, context mode, tools, cost class, and eligible roles—for example `sol-high`. |
| **Model registry** | Configuration listing available model profiles and their evaluated capabilities. |
| **Adapter** | Integration code that invokes a particular runtime such as Claude or Codex while preserving canonical inputs and outputs. |
| **Worker** | A generic executable stage. It may be agent-backed, such as an auditor, or deterministic, such as a schema validator. |
| **Orchestrator/controller** | Deterministic software that selects and sequences workers, manages state, enforces budgets, and handles retries and HITL pauses. |
| **Workflow/pipeline** | The declared ordering and dependencies between workers. The orchestrator executes it. |
| **Schema** | A machine-readable definition of a valid record. |
| **Record/artifact** | An immutable input or output, such as an input contract, review record, finding, decision, or closure record. |
| **Ledger** | The authoritative collection of adjudicated findings and their remediation state. |
| **Policy** | Rules governing routing, risk, authority, waivers, model usage, and stopping. |
| **Gate** | A deterministic policy check that permits, blocks, or pauses lifecycle progression. |
| **HITL** | Human-in-the-loop decision-making for intent, authority, exceptions, and risk acceptance. |
| **Evaluation harness** | Tests and measures skills, models, adapters, workflows, and policies using clean, seeded, and historical cases. |

## How the parts work together

```text
source documents + candidate plan
              ↓
      deterministic controller
              ↓
       immutable input contract
              ↓
classifier agent + classifier skill
              ↓
 review manifest + model assignments
              ↓
reviewer agents + reviewer skills
    executed through model adapters
              ↓
     review and finding records
              ↓
adjudicator agent + adjudicator skill
              ↓
       canonical finding ledger
              ↓
      HITL decisions if needed
              ↓
        reviser agent/worker
              ↓
 deterministic checks + re-review
              ↓
       exact-artifact closure gate
              ↓
      evaluation and feedback
```

The skill tells an agent how to perform a bounded task. The adapter starts that agent on a selected model. The agent produces a structured record. The controller validates the record and decides which stage runs next.

## How the eight components map to these things

1. **Common finding schema**

   Schemas and immutable review/finding records.

2. **Review input contract**

   Artifact freezer, context rules, permissions, and input records.

3. **Review-run orchestrator**

   Classifier skill, model routing, review manifest, lifecycle policy, and controller behavior.

4. **Adjudication and remediation ledger**

   Adjudicator skill plus canonical ledger.

5. **Final closure gate**

   Final-review skill plus deterministic approval checks.

6. **Evaluation and drift harness**

   Cases, graders, metrics, promotion gates, and drift monitoring.

7. **Human escalation and waiver policy**

   HITL rules, authority matrix, decisions, waivers, and risk acceptance.

8. **Post-implementation feedback loop**

   Conformance review, release records, observed outcomes, feedback, and learning actions.

## The two implementation designs

Both designs implement the same harness:

- **Controller-centric:** a purpose-built controller directly coordinates the workers.
- **Composable pipeline:** command-like workers are connected through a generic workflow runner.

The canonical components, skills, records, policies, models, and adapters are shared. Only the orchestration mechanism differs.

The most accurate description is:

> `review-plan` is a multi-model, policy-governed review harness composed of deterministic infrastructure and bounded agent-backed workers.

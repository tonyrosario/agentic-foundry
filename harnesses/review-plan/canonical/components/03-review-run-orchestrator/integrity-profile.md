# Canonical integrity profile

## Purpose

Define one interoperable hashing procedure for lifecycle records and referenced artifacts. Every `*_sha256` field uses this profile unless a field explicitly declares a different profile.

## Profile identifier

```text
canonical-json-sha256-v1
```

Records MUST carry this identifier beside their self-hash. Changing canonicalization or hash semantics requires a new profile identifier; implementations must never silently reinterpret an existing profile.

## Record hashing

Compute a record self-hash as follows:

1. Parse the record into the schema-defined logical data model. YAML is an authoring representation only.
2. Reject duplicate keys, custom YAML tags, aliases, non-string object keys, non-finite numbers, and values outside the schema.
3. Remove exactly the record’s self-hash field listed below. Do not replace it with `null`.
4. Retain `integrity.hash_profile` and every other field, including explicit `null`, empty arrays, empty objects, timestamps, prior-record hashes, and provenance.
5. Serialize the remaining value as UTF-8 JSON using RFC 8785 JSON Canonicalization Scheme semantics: deterministic object-key ordering, JSON primitive formatting, JSON string escaping, and no insignificant whitespace.
6. Compute SHA-256 over those exact UTF-8 bytes.
7. Encode the digest as 64 lowercase hexadecimal characters with no `0x` or `sha256:` prefix.
8. Store the digest in the excluded self-hash field.

Absent and explicit `null` are different values. Array order is significant. Unicode string contents are not normalized beyond canonical JSON escaping; producers must supply the intended Unicode value.

## Self-hash fields

| Record | Excluded self-hash field |
|---|---|
| Review input contract | `integrity.input_contract_sha256` |
| Authoritative source bundle | `integrity.source_bundle_sha256` |
| Classification record | `integrity.classification_record_sha256` |
| Review manifest | `integrity.manifest_sha256` |
| Lifecycle state record | `integrity.state_record_sha256` |
| Raw review record | `integrity.record_sha256` |
| Raw finding record | `integrity.finding_sha256` |
| Finding/remediation ledger | `integrity.ledger_sha256` |
| Final closure record | `integrity.closure_record_sha256` |
| Escalation/decision record | `integrity.decision_record_sha256` |
| Waiver record | `integrity.waiver_record_sha256` |
| Human authority matrix | `integrity.authority_matrix_sha256` |
| Cancellation and residual-obligation record | `integrity.cancellation_record_sha256` |
| Evaluation suite manifest | `integrity.manifest_sha256` |
| Evaluation case public envelope | `integrity.public_case_sha256` |
| Evaluation case sealed oracle | `integrity.oracle_sha256` |
| Evaluation run record | `integrity.evaluation_run_record_sha256` |
| Conformance review | `integrity.conformance_review_sha256` |
| Release-gate record | `integrity.record_sha256` |
| Feedback event | `integrity.feedback_event_sha256` |
| Learning action | `integrity.learning_action_sha256` |

A schema not listed here cannot claim a canonical record self-hash until the profile is versioned to include it.

## Artifact hashing

For a regular file, compute SHA-256 over its exact bytes. Do not normalize line endings, text encoding, whitespace, metadata, or archive format.

For an in-memory artifact with no file representation, serialize it under this canonical JSON profile and record the profile with the digest.

For a directory or evidence bundle, create a canonical bundle manifest containing sorted relative POSIX paths, entry type, byte length, and exact-file SHA-256. Reject absolute paths, `..`, duplicate normalized paths, and symbolic links unless the bundle schema explicitly defines link handling. Hash the canonical bundle manifest, not filesystem traversal order or archive bytes.

For a Git state, use the full immutable commit object ID in `repository_revision`. If SHA-256 is also required, hash an explicitly named exported artifact or canonical changed-surface manifest; do not relabel a Git object ID as SHA-256.

## Referenced-record validation

Every parent, prerequisite, governing record, and credited execution is stored as a canonical record reference or a schema-specific specialization containing the same fields:

```yaml
record_type: "review-record"
record_id: "rev-..."
record_sub_id: "revexec-..." # null unless the record has a composite logical identity
schema_version: "1.0"
logical_record_version: null # required only when the referenced schema defines one
record_sha256: "..."
lifecycle_id: "life-..." # null only for records that are intentionally lifecycle-independent
role: "completed-review"
```

`record_sub_id` carries `review_execution_id` for a raw review execution or another schema-defined secondary identity. `logical_record_version` carries values such as `review_manifest_version`, `ledger_version`, `decision_record_version`, or `waiver_record_version`; it is explicitly `null` for ID-plus-hash records with no logical version. `schema_version` is never substituted for `logical_record_version`.

Convenience IDs, status lists, and aggregate arrays are non-authoritative indexes. A gate may credit or validate a record only through a canonical reference tuple, and every repeated convenience value must match that tuple.

- Resolve the referenced record by its complete logical identity: record type, primary ID, secondary ID when defined, schema version, and logical record version when defined.
- Recompute its self-hash using the profile declared in that record.
- Compare the digest with the parent’s stored reference using exact lowercase hexadecimal equality.
- Verify shared `lifecycle_id` and repeated artifact hashes independently; a matching record hash does not excuse a foreign-key mismatch.
- Reject unknown profiles, missing hashes, mismatches, and records whose schema does not identify the self-hash field.
- Never resolve `active`, `current`, `latest`, a mutable status index, or supersession depth in place of the stored identity tuple.
- Reject a parallel ID/hash list as evidence of mapping unless each element is a keyed canonical tuple.

## Signatures and attestations

Signatures are separate records that reference the completed record hash, signer identity, authority, algorithm, and timestamp. A signature or audit-system receipt added after hashing is not embedded in the hashed record unless a later schema explicitly defines a new signed-envelope hash.

## Versioning

Never change this profile in place. A new algorithm, canonicalization rule, normalization choice, bundle format, or self-hash field set requires a new profile ID and compatibility policy. Existing hashes retain their original meaning permanently.

# Privacy review

Read this when the person asks for a privacy review, asks what personal-data harms a feature could cause, or asks for GDPR or CCPA/CPRA coverage of a design. It adds to the [threat-model method](../threat-model.md); the run folder, read-only rules, depth and checker are the same. The output supports a privacy assessment by the owner's privacy and legal people. It is engineering evidence, never legal advice or a compliance verdict.

## Pick the scope

| Request | `privacy.review_scope` | What runs |
| --- | --- | --- |
| "Privacy review of the export feature" | `privacy` | The privacy questions below in place of the six security questions. Choose the real architecture for topology, and set `privacy.security_analysis` to `not_run`. |
| "Threat model the export feature, privacy included" | `security-and-privacy` | Both question sets on one model, one `threat-model.json`. |
| Anything else | no `privacy` object | The ordinary security model. |

Depth works as in the method: `quick` is one pass with a self-check; `deep` adds a fresh-context challenge and treatment pass. Privacy is a review scope, never an architecture: `architectures.primary` still names web, api or another file from the [architecture selector](architecture-selector.md).

## Choose profiles

A profile adds regulatory questions to the engineering review. Start with none. Load one only when one of these holds, and record which in `selection.md`:

- the person names it ("check GDPR"), or
- the person or a project document says the system processes personal data of people in that jurisdiction: [GDPR](privacy-gdpr.md) for people in the EU or EEA, [CCPA/CPRA](privacy-ccpa-cpra.md) for California consumers. Record that statement as a `caller_claim` or `documentation` evidence record.

A hosting region, a language setting, a currency or a `country` column does not show where data subjects live. When the evidence only suggests a jurisdiction, keep the profile unloaded and add a gap naming the question for the owner. UK GDPR, other US states, LGPD, PIPEDA, COPPA and HIPAA have no profile here; name them as a gap when the scope suggests them, and leave the assessment to the owner's counsel.

Loading a profile never shows that the law applies. Applicability is the first topic in each profile and usually needs organizational facts the code cannot show.

## Gather privacy evidence

Do this during the evidence step, before analysis, inside the authorized scope. Record the category of data, never a value from code, fixtures or logs.

| Look at | Record |
| --- | --- |
| Logs, traces, error reporters | Which personal fields reach which sink, and any redaction before it. |
| Analytics and telemetry | The init call and event payloads, stable ids, consent gating, the visible recipient. A dependency in a manifest shows presence only. |
| Calls to third parties | The payload built, the recipient and the data categories. An unknown endpoint stays a gap. |
| Retention and deletion | Retention settings and jobs, soft-delete flags, purge paths and whether deletion reaches caches, search indexes, queues, exports and backups. |
| Collected fields | Each field's readers in the files you read. Write "no reader found in the inspected files", never "unused". |
| Identifiers | Ids reused across sessions, products, tenants or recipients. |
| Sensitive categories | Health, location, biometrics, children's data or anything the project labels sensitive, attributed to where it is labeled. |

A deleted primary row is not deletion everywhere, a checkbox is not consent, and a missing policy document is a gap, not a defect.

## Ask the privacy questions

For each processing activity the evidence supports, ask who is affected and how processing, even authorized processing, could harm them:

- Collection beyond the purpose, or a purpose that drifts to a new use.
- Linking or re-identifying people across contexts; inference of sensitive traits.
- Disclosure to a recipient beyond what people were told, including a vendor's own reuse.
- Choices that mislead, cannot be withdrawn, or do not reach downstream copies.
- Over-retention, and deletion or correction that misses a copy.
- Profiling or automated decisions with an effect on people and no route to contest.

An authorized recipient's harmful reuse needs no attacker: the actor is the recipient, with its capability stated. Each scenario still needs an asset, actor, reachable path, prerequisites, counterevidence and a deciding observation, as in the [artifact contract](artifact-contract.md).

## Record it in the existing model

Use the records the checker already reads, plus one `privacy` object. The full shape is in the [artifact contract](artifact-contract.md#privacy-records).

- **Processing activities and personal data** are `assets` with `kind` `processing_activity` or `personal_data`; put purpose, affected people, retention and the supplied legal role in `description`.
- **Affected people and recipients** are `actors` with a stated `capability`.
- **Flows** list the personal data they carry. Map each privacy boundary to a guide row; most fit "Resource and data lifecycle" or "Jobs, queues and external providers".
- **Privacy threats** use the normal status words and handoffs. An unconfirmed deletion path is a `design_hypothesis` with a gap.
- **Profile coverage** goes in `privacy.coverage`: an `applicability` row citing the claim or document that selected the profile, then rows per topic and processing activity, with status `assessed`, `partial`, `not_assessed` or `not_applicable`. `assessed` means the question was examined, not that the system complies. `not_applicable` needs evidence. Missing organizational facts keep a row `partial` and add a gap.

`report.md` adds a processing inventory (data, people, purposes, recipients, flows, retention, deletion, unknowns) and, only for selected profiles, a coverage table, both derived from the JSON. It ends with the questions for the owner's privacy and legal reviewers, and says plainly that it is not legal advice and supports, but is not, a DPIA or privacy risk assessment.

## Deep, challenge and change

A deep challenge also tests applicability claims, missing lifecycle paths, affected groups such as children or employees, and harms from authorized use. Treatments favour collecting less, restricting purpose, separating data, deleting on schedule, honest choices and recipient limits. Verification plans use synthetic records only, stay `not_run`, and cover rights requests, withdrawal reaching downstream copies, deletion across derived data and restored backups, and retention expiry.

A [change review](change-reviewer.md) of a model with a `privacy` object keeps its scope, profiles and coverage rows, and compares new data categories, recipients, purposes, retention and log or telemetry sinks. A new recipient for existing data can matter even when sign-in is unchanged.

## Methods

LINDDUN GO and PRO are separate procedures and are not bundled. Run one only when the person asks and supplies material they may lawfully use; otherwise record the gap. A privacy review here does not claim a LINDDUN run. See [method notes](method-notes.md).

## Worked failure

Request: "privacy review of account deletion, we serve EU users". A first draft loads GDPR, marks `privacy:gdpr:rights` `assessed` because `DELETE /account` removes the user row, and calls erasure compliant. That fails: it reads one store and states a legal conclusion.

The corrected pass records the caller claim about EU users, loads GDPR only, and reads further. Delete sets `deleted_at` (`src/account/delete.ts:18-31`), the nightly analytics export filters nothing (`jobs/export.ts:40-52`), and the search index was not supplied. It records `T1` as an `observed_weakness` (deleted users keep flowing to the analytics vendor) handed to audit, a gap for the search index, and `privacy:gdpr:rights` as `partial`: erasure reaches neither the export nor, as far as known, the index, and whether the vendor is a processor is an owner question. The report sends the rights and processor questions to the owner's counsel. (Synthetic paths.)

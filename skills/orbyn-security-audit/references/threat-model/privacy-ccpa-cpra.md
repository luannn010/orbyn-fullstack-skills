# CCPA/CPRA profile

Load this only under the profile rule in [privacy review](privacy.md#choose-profiles). Profile id `ccpa-cpra`; coverage lenses are `privacy:ccpa-cpra:<topic>`. It covers the California Consumer Privacy Act as amended by the CPRA, and its regulations, as one profile. "CCPA" or "CPRA" alone selects it.

The questions help engineers gather evidence for the owner's privacy and legal reviewers. They are not legal advice. Section pointers were taken from the source library, which read the statute and regulations effective 1 January 2026 in November 2026. Dates and thresholds change: read the [CPPA regulations index](https://www.cppa.ca.gov/regulations/) yourself only when network access is authorized, record what you read, and otherwise mark every timing statement as not checked in this run.

## Topics

Write coverage rows per topic and processing activity; the checker accepts only the topic ids below.

| Topic | Questions for the evidence | A `not_run` check to propose |
| --- | --- | --- |
| `applicability` | California consumers, business thresholds for the period, entity relationships, exemptions (Civil Code 1798.100 to 1798.145). Needs owner facts. | Test each claimed exemption against each data category. |
| `notice` | Do notices match the actual categories, purposes, recipients and retention? | Trace a new SDK field to its disclosure. |
| `access-correction-deletion` | Can requests find, return, correct or delete the data across stores, derived data, backups and vendors? | Synthetic requests across each store. |
| `sale-sharing` | Which relationships count as sale or sharing, and do opt-outs and preference signals reach them, including age-related consent? | Propagate a signal through an anonymous session and an account. |
| `sensitive-information` | Which sensitive personal information is used, and does a limit request reach analytics and recipients? | Trace a limit request downstream. |
| `nondiscrimination` | Does exercising a right or refusing optional processing change service or incentives (1798.125)? | Compare two synthetic user paths. |
| `purpose-retention` | Are collection, use, disclosure and retention tied to stated purposes? | Follow an expired synthetic record through queues and restores. |
| `choice-request-handling` | Are choices symmetric and free of dark patterns? Do opt-out and limit requests avoid needless identity checks while verified requests resist impersonation? | Pass, fail and inconclusive outcomes for each request type. |
| `recipient-contracts` | Do recipients' observed behavior and supplied contract terms match their role (service provider, contractor, third party)? | Trace opt-out, correction and deletion across the recipient boundary. |
| `security-breach` | Which safeguards protect the information, and how do detection and recipient coordination work (1798.100(e); 1798.150 is narrower)? | A synthetic incident timeline. |
| `california-security-screening`, `california-breach-screening` | Screening only for the separate security and breach-notice duties (1798.81.5, 1798.82). | Name the entity, data, incident conditions and deadlines that need confirmation. |
| `risk-assessment` | Does any activity need a risk assessment under the regulations, and when? | Name the processing changes that would need one. |
| `cybersecurity-audit` | Does an independent audit duty apply? A code review is not that audit. | List the scope and independence evidence needed. |
| `admt` | Is automated decision-making technology used for a significant decision, with notice, opt-out and access? Not all automation is covered. | Walk a synthetic adverse outcome and an opt-out. |

## Limits

Write at least the `applicability` row, citing the claim or document that put the profile in scope. List each topic you did not examine as `not_assessed` with a reason. Every other status cites evidence. A supported engineering concern is not a statutory violation, and a future compliance date does not remove the harm to people. The Delete Act, data-broker rules and other California sector laws are outside this profile; name them as a gap when the scope suggests them. Every conclusion that depends on law goes to the owner's counsel.

# GDPR profile

Load this only under the profile rule in [privacy review](privacy.md#choose-profiles). Profile id `gdpr`; coverage lenses are `privacy:gdpr:<topic>`. It covers the EU General Data Protection Regulation (Regulation (EU) 2016/679). UK GDPR, national rules and sector law are outside it.

The questions help engineers gather evidence for the owner's privacy and legal reviewers. They are not legal advice. Article pointers were taken from the source library as reviewed in November 2026; read the [regulation text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) yourself only when network access is authorized, and record what you actually read as evidence. Otherwise record the source as not read in this run.

## Topics

Write coverage rows per topic and processing activity; the checker accepts only the topic ids below. A row may cover several activities only when its reason names them and their common basis.

| Topic | Questions for the evidence | A `not_run` check to propose |
| --- | --- | --- |
| `applicability` | Which people, roles and Member States are involved, and does any exclusion apply (Articles 2 to 4)? Usually needs owner facts. | None; list the facts the owner must supply. |
| `lawful-basis` | Which basis does the owner claim for each purpose (Article 6)? Does a secondary use stretch it? | Follow a purpose change through queued work with a synthetic record. |
| `consent` | Where consent is relied on: what is asked, what is stored as proof, can it be withdrawn, and does withdrawal reach downstream copies (Article 7)? | Withdraw on a synthetic account and trace each consumer. |
| `sensitive-children` | Special-category or criminal-offence data, or a service used by children (Articles 8 to 10)? | Trace the labeled field to every reader. |
| `purpose-minimization` | Which fields, inferences and recipients does each purpose need (Article 5)? | Trace one optional field from collection to every consumer. |
| `accuracy` | Do corrections reach derived records and decisions? | Correct a synthetic record and list the expected downstream changes. |
| `retention` | What justifies each period, and does disposal reach backups, logs and embeddings? | Expire a synthetic record across replicas and a restore. |
| `transparency` | Do the supplied notices match the modeled purposes, sources, recipients and flows (Articles 12 to 14)? | Compare the notice version with the collection and disclosure paths. |
| `rights` | Can access, correction, erasure, restriction, portability and objection requests find all the data, with proportionate identity checks (Articles 15 to 21)? Account removal is not erasure everywhere. | Synthetic requests: legitimate, impersonated, lawful exception, partial vendor deletion. |
| `automated-decisions` | Is there profiling or a decision with a significant effect, human involvement and a route to contest (Article 22)? | Review a synthetic adverse decision end to end. |
| `design-defaults` | Are defaults, access and collection bounded to the purpose (Article 25)? | Compare new-account defaults and privileged overrides. |
| `processors` | Do the roles, instructions and subprocessors the owner supplies match the observed flows (Article 28)? | Trace a rights request across the vendor boundary. |
| `accountability` | Are processing records and responsibility documented, and is a DPO needed (Articles 30, 37 to 39)? | Compare the inventory with the supplied records. |
| `security-breach` | Which safeguards and detection protect people, and who must notify whom (Articles 32 to 34)? | A synthetic incident timeline separating controller and processor duties. |
| `dpia` | Is high-risk processing screened, with necessity, risks and safeguards documented (Article 35)? | Name the changes that would need a new assessment. |
| `transfers` | Which recipients and destinations are outside the EEA, and what transfer mechanism is supplied (Articles 44 to 49)? Encryption or a vendor's location does not show one. | Add a synthetic destination and check the restriction holds. |

## Limits

Write at least the `applicability` row, citing the claim or document that put the profile in scope. List each topic you did not examine as `not_assessed` with a reason. Every other status cites evidence. A finished row says what the evidence shows; whether that meets the regulation is the owner's counsel's call. DPIA material here supports a formal assessment and never replaces one.

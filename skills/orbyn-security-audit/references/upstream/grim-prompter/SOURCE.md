# Selected Grim Prompter source record

This is an inactive provenance record, not an agent entrypoint. Part of the threat-model
mode of this skill derives from Grim Prompter, copyright Manicode Security (MIT), at
<https://github.com/jmanico/grim-prompter/tree/2a94457c7bc63ffbc4a44ea50ae645ab8cee26bf>.
Earlier pins named the holder Jim Manico; upstream commit b5376f7 changed the copyright line
to Manicode Security with the MIT grant unchanged.
`LICENSE` is the upstream notice, unchanged. `LICENSE-Orbyn.txt` covers Orbyn adaptations
and additions. Use the maintained `orbyn-security-audit` skill. `source-manifest.json` lists
each maintained file with its upstream path and its original and maintained hashes.

Upstream is an agent-facing prompt library: 36 architecture quick prompts, 36 six-stage
deep chains, 29 method prompts, five helpers, shared references, a runbook and, since
32e7821, a privacy review scope with quick and six-stage deep prompts and GDPR, CCPA/CPRA
and other-regime screening profiles. It states
that its method text is written in its own words and does not reproduce method sources.
The selection below follows what changes a decision in this library, not a count.

## Kept and adapted

- The runbook's operating boundary became `references/threat-model.md`: read-only
  inspection, the guarded Git forms, evidence by `path:start-end`, no fabricated system
  facts or results, secrets replaced by placeholders, artifacts in a run folder.
- Helpers, shortened to their working rules: `architecture-selector.md` (with the
  composition guide's ownership and identity rules), `method-selector.md`,
  `evidence-guide.md`, `model-challenger.md`, `change-reviewer.md`.
- The artifact contract, reduced to the records the library uses (`artifact-contract.md`).
- Tool and shared credential boundaries (`tool-credential-boundaries.md`), kept because
  agent tools, MCP servers and shared service identities are a boundary this library meets.
- Twelve quick prompts, each reduced to its boundary checks, scenario families and
  proposed checks: web, api, multi-tenant-saas, agentic-ai, rag, cicd-supply-chain,
  cli-developer-tools, desktop, mobile, serverless, microservices, data-platform.
- `method-notes.md`, from the README's note that method names belong to their owners, and
  the LINDDUN PRO method's note that its tutorial reserves reproduction rights.
- The privacy scope, condensed into `privacy.md`: the privacy README and quick prompt, the
  analysis, evidence and profile patterns, and the list of regimes the screening profile
  names. Privacy is a review scope, not an architecture; profiles start empty.
- The GDPR and CCPA/CPRA profiles, condensed into `privacy-gdpr.md` and
  `privacy-ccpa-cpra.md`: stable topic ids, evidence questions and proposed checks.
- The privacy additions to the helpers and the artifact contract at 2a94457.

## Original to Orbyn

`scripts/check_threat_model.py` (including its checks of the `privacy` object),
`scripts/threats_to_ledger.py`, the join with
`references/threat-boundaries.md` (each model boundary names one of its rows), the status words, the handoff to audit, remediation and
verification, and every edit to the two security entrypoints.

## Excluded, never copied

- The 36 six-stage deep chains (252 files, about 7.5 MB). Their stages pass cumulative JSON
  envelopes with identity, change and chunk bookkeeping; the architecture-specific content
  is already in the quick checks. Deep depth here is the quick pass plus a fresh-context
  challenge and treatment pass.
- The other 24 quick prompts: ai-ml, batch-workflows, blockchain-smart-contracts,
  browser-extension, cloud-control-plane, collaboration-realtime, container-platform,
  content-media-delivery, cyber-physical-robotics, embedded-firmware, enterprise-integration,
  event-driven, high-assurance-isolated, hybrid-multicloud, identity-federation, iot-edge,
  modular-monolith, monolith, offline-first-sync, ot-ics, payments-transactions,
  peer-to-peer, real-time-streaming, service-oriented. This library has not met those
  boundaries; the neutral baseline covers them until a real case earns a file.
- All 29 method prompts (about 880 KB). They name third-party methods and catalogs with
  their own terms: ATT&CK, CAPEC and ATLAS (MITRE trademarks and terms of use), the Cyber
  Kill Chain (Lockheed Martin trademark), CVSS (FIRST), the LINDDUN and Elevation of
  Privilege decks (Creative Commons), Trike (its own methodology notice) and MAESTRO (a
  vendor article). `method-notes.md` records the owners and the rules instead.
- The six privacy deep stages, `privacy/examples.md`, `privacy/acceptance-walkthrough.md`
  and `MODELS.md`. Deep privacy here is the quick pass plus the fresh-context challenge and
  treatment pass; the worked failure in `privacy.md` is Orbyn's own.
- `privacy/profiles/other-regimes-screening.md` as a profile: its regimes are named as gaps
  for the owner's counsel instead of a screening procedure.
- The `DATA_INVENTORY.md` companion and its rendering and continuation rules. The processing
  inventory is a section of `report.md`, derived from the JSON.
- The shared envelope machinery: identity maps, change declarations, chunk and
  continuation protocols, and the pattern files for each deep stage.
- `README.md`, `start-here.md`, `catalog.md`, `logo.svg`, the skill file for the upstream
  host, `AGENTS.md`, `.gitignore`, and every instruction to clone, link or load the
  library into an agent's own skills folder.

## Changed

- Output goes to an ignored run folder in the outer workspace, never into the target, and
  is never published. A threat model of a private target describes how to attack it.
- Authority is ours: no scan or test of a live system, no exploitation, no credential use,
  no publication, and security work on the lead tier.
- Threats carry a `basis` of observed weakness, design hypothesis or protected, and hand
  off to audit, remediation or a decision. Severity belongs to a confirmed audit finding.
- Privacy findings use the existing records plus one `privacy` object (scope, selected
  profiles, coverage rows), not Coverage and Requirement records. A profile loads only when
  the person names it or the system processes personal data of people in that jurisdiction,
  and every profile output is evidence for the owner's counsel, never legal advice.
- Verification stays `not_run` in this mode. A fresh verifier closes the loop after
  remediation.
- `scripts/check_threat_model.py` checks the records and, against the target, that each
  cited line range exists. Each model boundary names a row of the boundary guide, and the
  architecture checks add to those rows.

Upstream install steps and host-specific commands are not imported or activated. Source
identity is not runtime proof, and no upstream prompt was run.

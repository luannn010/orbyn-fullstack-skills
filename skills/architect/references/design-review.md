# Review the design before code

A finding in a design document costs a paragraph to fix; the same finding in a PR
costs a rewrite. When a written design will drive a substantial build (new owner,
public contract, data shape, migration or a change several people or agents will
implement), review the document before any code. A small clear change skips this.

## Give reviewers the document, not the conversation

The author holds the whole conversation, so the author cannot see what the document
leaves out. Each reviewer is a fresh child that gets only:

- the design document,
- the files it links to inside the workspace,
- any other file or saved web page the user approves (save a web page as a local
  file; some reviewers cannot open URLs).

Never pass the chat, your own verdict or the alternatives you already rejected
unless the document records them. A review in the author's own context is a
self-check, not a fresh review; say so if no child can run.

## Four lenses

Run the lenses as read-only reviewer children at the resolved `reviewer` tier, within
the [delegation limits](../../orbyn-workflow/references/lead-contract.md#review-before-the-pr).
With the default 2 + 1 slots, use three children: zoom out with design critic,
comprehension alone, and implementation readiness. Keep comprehension separate,
because a reader who already checked the code is no longer naive.

| Lens | Asks | A blocker is |
| --- | --- | --- |
| Zoom out | Do we need this now? Does an existing owner, library or service already solve most of it? Is this a dead end? Is the document lost in implementation detail? | Building something an existing owner already provides, or a design that blocks the obvious next requirement |
| Design critic | Which assumptions lack evidence? What fails, and how does it recover? What happens at expected scale, with revoked access or a retry? What does it cost to run: model tokens, API quotas and rate limits, storage, hosting? Write each risk as an [interrogate](../../interrogate/SKILL.md) scenario. | A failure with no recovery path, or a paid or rate-limited path with no estimate or limit |
| Comprehension | Can a new reader restate what this proposes and how the current system works? Use the [paraphrase test](../../interrogate/SKILL.md#paraphrase-a-document-first). Are the [template](design-doc-template.md) sections present, or their absence explained? | A section the reader cannot restate, or a missing failure, cost or migration section |
| Implementation readiness | Could a worker build this without making a design decision? Are the contract, files in order, the failing test first, risks, rollback and stopping condition named? Does it say how stored data and released callers move ([migration](../../orbyn-data-migration/SKILL.md))? Spot-check that the files and symbols it names exist and behave as described. | A step that forces the builder to choose an owner, data shape or failure behavior, or a format change with no migration |

For a design read beyond the team, the lead also runs [unslop](../../unslop/SKILL.md)
on it: plain words, and every claim about current or tested behavior matching its
evidence.

## Run it in stages

Run the lenses in order, because each one changes what the next should read:
zoom out and design critic on the whole document, then comprehension, then
implementation readiness on the build plan. The lead asks the user once which way to run it:

| Mode | Runs | Use when |
| --- | --- | --- |
| Step by step (default) | Each stage, then a checkpoint | The design is still moving |
| One report | All three stages without stopping, then one combined report | The author is away or wants one pass |
| Design only | Zoom out, design critic and comprehension; no readiness | There is no build plan yet |
| Readiness only | The build-plan section alone | The design was already approved |

Write each stage's findings to a file in the task's ignored output folder
(`output/<task>/design-review/zoom-out-critic.md`, `comprehension.md`, `readiness.md`).
In chat, give the path and the count of blockers, majors and nits, never the whole
report. One report mode adds `summary.md`: findings merged and deduplicated, ranked
blocker, major, nit, each linked to the raw findings it came from.

After each stage, ask one question with these choices: continue to the next stage;
resolve the findings now; pause while the author edits the document; stop. After
edits, re-run that stage once. If blockers remain, put them to the user, who accepts
each as a trade-off (recorded in the document) or sends it back; never accept one
silently. The three-round cap below still bounds the whole review.

## Screen for red flags

Before choosing between candidate shapes, check each one for these. Read it as the
next contributor will: an agent that sees only the files it opened, copies the
nearest example and takes the shortest path that compiles. Prefer the shape where an
edit that looks right from one file is right for the whole repository.

- **Shallow module:** see [maintainable modules](maintainable-modules.md).
- **Information leakage:** a representation, policy or wire format appears in more
  than one module, so changing it needs coordinated edits. Parse external data into
  domain types at the boundary and keep transport types private.
- **Temporal decomposition:** load, validate, transform and save as separate modules
  that each repeat one representation. Group by the knowledge owned, not run order.
- **Split ownership:** two modules write the same state or keep their own copy.
  Give the state one owner that others ask.
- **Two ways to do one task:** each keeps gaining callers. Keep one, move callers,
  delete the other in the same change.
- **Importable internals:** what an outside caller can import becomes interface.
  Make it unreachable from outside so the build fails.
- **Hand-synced lists:** adding an item means editing several lists. Derive them from
  one, or fail the build when they disagree.

A flag is a reason to revise or reject the shape, not a style note. For example, a
sync design with a client cache and a server table that both decide conflict rules
fails split ownership: the next fix lands in whichever file the agent opened.

## Resolve, then build

Reply to every finding with a fix or a contest backed by evidence the reviewer can
read, as in [make review rounds converge](../../orbyn-workflow/references/engineering-scope.md#make-review-rounds-converge).
Re-review only what changed, and stop after three rounds. The user approves the
design; the approved document is what the build and its PR reviewer check against.

Synthetic example: a webhook-delivery design says "failed deliveries are retried".
The comprehension reader cannot restate when a retry stops or what happens to a
duplicate event, so that section is a blocker. Zoom out finds the existing job queue
already gives retries with backoff. Implementation readiness asks which owner records
the delivered event ID. The revised design reuses the queue, names the dedupe owner
and states the retry limit before any code exists.

Red-flag screen adapted from Lauren Tan's pstack
[design red flags](https://github.com/cursor/plugins/blob/bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7/pstack/skills/architect/references/design-red-flags.md)
(MIT), revision `bf0c7cd`; see the [MIT notice](principles/LICENSE.txt).

Reviewed inspiration, observed 9 November 2026:
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model/tree/e9e1f06aa4e26e95cd4ed37210a0632202c429e9)
(Apache-2.0). Independently written; no upstream text, prompts or tooling imported.

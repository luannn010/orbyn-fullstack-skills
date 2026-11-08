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

## Three lenses

Run each lens as a read-only reviewer child at the resolved `reviewer` tier, within
the [delegation limits](../../orbyn-workflow/references/lead-contract.md#review-before-the-pr).
When the limit is tight, one child may hold two lenses; keep comprehension separate,
because a reader who already checked the code is no longer naive.

| Lens | Asks | A blocker is |
| --- | --- | --- |
| Zoom out | Do we need this now? Does an existing owner, library or service already solve most of it? Is this a dead end? Is the document lost in implementation detail? | Building something an existing owner already provides, or a design that blocks the obvious next requirement |
| Comprehension | Can a new reader restate what this proposes and how the current system works? Use the [paraphrase test](../../interrogate/SKILL.md#paraphrase-a-document-first). | A section the reader cannot restate |
| Implementation readiness | Could a worker build this without making a design decision? Are the contract, files in order, the failing test first, risks, rollback and stopping condition named? | A step that forces the builder to choose an owner, data shape or failure behavior |

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

Reviewed inspiration, observed 9 November 2026:
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model/tree/e9e1f06aa4e26e95cd4ed37210a0632202c429e9)
(Apache-2.0). Independently written; no upstream text, prompts or tooling imported.

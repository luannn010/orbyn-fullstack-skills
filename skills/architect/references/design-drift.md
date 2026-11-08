# Check designs against what was built

A design or README that no longer matches the code misleads every later reader and
agent. A drift check compares the checked-in documents with the current source (or,
for product UI, with the built app) and reports each difference with an anchor on
both sides. It changes nothing; the user decides what to fix.

## Run it

1. **Choose the documents.** A folder of designs or READMEs the user names, or the
   designs a change claims to implement. Pin the source revision you compare against.
2. **Map each document to code.** Use the files and symbols it names. Where it names
   none, find the routes, functions or components it describes with
   [how](../../how/SKILL.md), and note that the document should link them so the next
   check is cheaper.
3. **Compare and classify** each difference:

   | Kind | Means | Usual fix |
   | --- | --- | --- |
   | Missing | The document describes behavior the code does not have | Build it, or mark it not done |
   | Changed | Both exist, but they disagree (limits, states, order, errors, names) | Decide which is right |
   | Extra | The code does something consequential the document never mentions | Document it, or remove it |
   | Moved | Same behavior under a new file, symbol or route | Update the links |
   | Unverifiable | Needs runtime, data or a device you cannot reach | Name the check that would settle it |

4. **Write the report** to `output/<task>/drift/report.md`: per document, each finding
   with its kind, the document line, the code anchor (file and symbol) and one
   sentence of impact. In chat, give the path and the counts by kind.

Never resolve drift by rewriting the document to match the code without asking: the
document may be right and the code wrong. A difference that a recorded decision
explains is not drift; cite the decision.

## Designs against the built product

For UI, compare the design artifacts (screens, every state, copy, window chrome)
with screenshots of the built app on its real surface (building and running it needs
the user's scope; without it, compare against existing screenshots and say so), using
[visual review](../../orbyn-ui-design/references/visual-review.md). A browser
preview cannot show native chrome, so a desktop shell is compared on the built
window. Report each difference the same way, with the design frame and the built
screenshot as the two anchors.

Synthetic example: the delivery design says retries stop after five attempts and
duplicates are dropped by event ID. The code retries forever (changed), drops
duplicates as designed, and also pauses a webhook after ten failures (extra). The
report names both with anchors, and the user decides the retry limit is a bug and
the pause should be documented.

Reviewed inspiration, observed 9 November 2026:
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model/tree/e9e1f06aa4e26e95cd4ed37210a0632202c429e9)
(Apache-2.0). Independently written; no upstream text, prompts or tooling imported.

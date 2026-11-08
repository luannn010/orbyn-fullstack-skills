# Design document template

Use these sections for a design that will drive a substantial build. Keep each one
short; write "Not applicable" with a reason rather than deleting a section, so a
reviewer can tell an omission from a decision. The project's own template wins.

1. **Problem.** What is wrong or missing, for whom, and the evidence.
2. **Goals and non-goals.** What done means, and what this deliberately leaves out.
3. **Current system.** How it works today, with file and symbol links.
4. **Proposal.** Owners, interfaces, data shapes and state transitions; one
   representative call and its result.
5. **Alternatives rejected.** Each with the reason.
6. **Failure and recovery.** Partial failure, retry, stale or revoked access, and how
   a user or operator recovers.
7. **Cost and limits.** Model tokens, API quotas and rate limits, storage and hosting
   at expected volume, with the estimate and how it is capped.
8. **Migration and compatibility.** Stored data, released callers and clients, and
   the order of change.
9. **Security and privacy.** Authority, secrets and personal data touched.
10. **Build plan.** Files in order, the failing test first, risks, rollback and the
    stopping condition.
11. **Open questions.** What is undecided, and who decides.

Review it with [design review](design-review.md) before code.

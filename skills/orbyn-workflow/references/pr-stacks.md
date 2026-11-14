# Stacked pull requests

A stack is a chain of PRs in one repository: the bottom PR targets the trunk (usually
the default branch) and each PR above targets the branch below it, so every PR shows
only its own layer's diff. Use one when the next change depends on code that is not
merged yet; independent work goes in its own PR from the trunk instead
([build while waiting](../playbooks/build-while-waiting.md)).

## Design the layers

- One concern per layer, ordered by dependency: shared types and schema lowest, the
  code that uses them above, tests with the layer they test. A layer depends only on
  its own branch or lower ones, and builds and passes its checks on its own.
- A stack at most two PRs deep by default, within the lead's open-PR limit
  ([stack limits](../playbooks/build-while-waiting.md#stack-only-what-depends-on-n)).
  A third layer (schema, then API, then UI) waits until the bottom one lands, unless
  the user raises the limit.
- Stacks are linear. Two pieces that both depend on the same base but not on each
  other are two stacks, or one waits.

## Choose the mechanism

1. **GitHub native stacks, when available.** GitHub links the PRs as a stack, shows a
   stack map, applies the trunk's required checks and branch rules to every layer,
   and retargets the remaining layers after a lower one merges; sync the local
   branches afterwards. All branches must be in the same repository. Use the
   `gh stack` extension when already installed; never install it implicitly.
   Commands, exit codes and recovery are in the pinned
   [gh-stack skill](upstream/gh-stack/SOURCE.md). Use non-interactive forms; never
   run `modify` or `switch`, which wait for keyboard input. Exit code 9 means stacks
   are not enabled for the repository: tell the person. Do not merge with
   `gh stack merge`: it cannot pin an expected head, and without a method flag it
   reuses the last-used one. Merge as described below.
2. **Plain Git otherwise.** Cut each branch from the one below and open each PR with
   the branch below as its base; name the base PR in the description, since there is
   no stack map. When the trunk moves, run `git rebase --update-refs <trunk>` from the
   top branch (Git 2.38 or later), then `git push --force-with-lease` each changed
   branch. `--update-refs` skips a branch checked out in another worktree: rebase
   that one in its own worktree, bottom-up.
3. **From a fork, neither works,** because a PR's base must be a branch in the
   upstream repository. Wait for the base PR, or open the dependent PR against the
   trunk as a draft that says it depends on the base PR; it carries the base PR's
   commits until that PR lands, then rebase it.

## Authority

- Run `submit` only once every layer it would open has had its review; it opens a PR
  for every branch, and drafts still count as opened PRs. Opening a stack needs the
  same PR authority as opening one PR.
- **Native stacks: merging a layer merges every unmerged layer below it.** Check that
  authority covers every PR that would land. A request to merge one PR at a time does
  not authorize merging an upper PR together with its lower layers. In this skill
  library, no PR an agent asked for may be merged by an agent, so a stack containing
  one waits for a human. Follow the native merge procedure below.
- **Plain Git: merging an upper PR merges it into the branch below,** not the trunk;
  that is not delivery.
- Stack merges are asynchronous, and with a merge queue they queue: read back the
  merged state before reporting anything landed.
- `unstack` without `--local` removes the stack on GitHub too; it, and any rewrite of
  someone else's stack, needs that stack owner's agreement.

## Merge a native stack safely

Detect native stack metadata and resolve the actual lowest **open** downstack PR
before each action; its original numeric position may be stale after a merge.
Re-read its exact head, base, checks, reviews and repository rules. Apply the
[current-head CI and review gates](../playbooks/pr-iteration.md#dependent-stacks-and-current-context)
to each layer; do not use ordinary `gh pr merge` or the ordinary REST merge
endpoint as the native stack merge path.

Merge only that lowest open PR, through GitHub's async REST endpoint: `PUT
/repos/{owner}/{repo}/pulls/{number}/merge-async`, with `sha` pinned to its
verified head. The pin covers the targeted PR only; targeting an upper PR would land
the layers below it unpinned. Set `bypass_rules: false`, unless the
[owner bypass](../playbooks/opening-a-pr.md) applies to this exact PR (a review rule
on the user's own PR, never a failing or missing check). For a direct merge, specify the repository's intended
`merge_method` explicitly. Respect a configured merge queue: use its supported
default or queue action, never bypass it to force a direct merge. Recheck the
repository's rules and API support before sending.

A `200` means the PR was already merged or is already queued: read its state, do
not resend. A `202` supplies a pending result UUID; retrieve it with `GET
/repos/{owner}/{repo}/pulls/{number}/merge-async/{uuid}`. A `409` means a merge
request is already pending; its body carries that request's UUID and options. Check
its expected head and options before relying on it, and do not send a duplicate. A pending result is not a merge.
An `enqueued` final async result is also not a landing and will not later change to
`merged`. For every result claiming a merge, including after a queue completes,
independently read the PR's merged state, actual base, landing commit and tree.
Stop on a changed head, unexpected content or an
unverifiable pending operation and reassess before another effect. If a UUID expires
or returns `404`, reconcile current PR state once before any newly authorized retry.

GitHub references, observed 2026-11-14: [async merge](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously),
[async result](https://docs.github.com/en/rest/pulls/pulls#get-the-result-of-an-asynchronous-merge),
[stack API](https://docs.github.com/en/rest/pulls/stacks), and
[merging stacked pull requests](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests).

## Keep it current

- Native: wait for GitHub to retarget after a lower layer lands, then refresh source,
  ancestry and context; `gh stack sync` updates the local branches when the extension
  is installed. Native sync or rebase can rewrite branches and update a
  worktree: check authority and branch/worktree ownership first. If the CLI is
  missing, GitHub's **Rebase stack** web action is an option when authorized. Do
  not automatically use plain-Git update-branch or force-push on a native stack.
- Plain Git, after a lower layer was squash-merged: from the top branch,
  `git rebase --update-refs --onto <trunk> <old parent head SHA>` (the SHA recorded
  when the child was cut), push with `--force-with-lease`, then retarget the child
  PR's base to the trunk within your authority.
- Either way, require fresh-head CI for every changed head, even when its tree is
  identical; earlier head results cannot gate the new head. Compare contents after
  a rewrite and seek review of unexpected changes. Equal trees do not preserve all
  review or other verdicts. Repeat affected checks ([dependent stacks](../playbooks/pr-iteration.md#dependent-stacks-and-current-context)).
  A fix that belongs to a lower layer goes on that layer.
- Stack branches may live in separate worktrees; never steal another worktree's
  checkout ([orbyn-worktree](../../orbyn-worktree/SKILL.md)).

## Review

Each layer gets its review before its PR opens, like any PR
([review before the PR](lead-contract.md#review-before-the-pr)); the reviewer reads
that layer's diff against the branch below, not against the trunk. Re-review a layer
whose contents changed in a rebase beyond a clean replay.

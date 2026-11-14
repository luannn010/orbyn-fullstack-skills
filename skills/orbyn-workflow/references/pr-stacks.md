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
   `gh stack` extension when it is already installed; installing it
   (`gh extension install github/gh-stack`) is a tool install, so ask the person
   first. Commands, exit codes and recovery are in the pinned
   [gh-stack skill](upstream/gh-stack/SOURCE.md). Always use its non-interactive
   forms (`view --json`, `submit --auto`, `merge <target> --yes`); never run
   `modify` or `switch`, which wait for keyboard input. Exit code 9 means stacks are
   not enabled for the repository: tell the person.
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
  merge authority covers every PR that would land, and pass the repository's merge
  method explicitly (`gh stack merge` otherwise reuses the last one). In this skill
  library, no PR an agent asked for may be merged by an agent, so a stack containing
  one waits for a human.
- **Plain Git: merging an upper PR merges it into the branch below,** not the trunk;
  that is not delivery.
- Stack merges are asynchronous, and with a merge queue they queue: read back the
  merged state before reporting anything landed.
- `unstack` without `--local` removes the stack on GitHub too; it, and any rewrite of
  someone else's stack, needs that stack owner's agreement.

## Keep it current

- Native: after the trunk moves or a lower layer merges, `gh stack sync`.
- Plain Git, after a lower layer was squash-merged: from the top branch,
  `git rebase --update-refs --onto <trunk> <old parent head SHA>` (the SHA recorded
  when the child was cut), push with `--force-with-lease`, then retarget the child
  PR's base to the trunk within your authority.
- Either way, repeat each moved layer's affected checks; earlier results no longer
  apply ([dependent stacks](../playbooks/pr-iteration.md#dependent-stacks-and-current-context)).
  A fix that belongs to a lower layer goes on that layer.
- Stack branches may live in separate worktrees; never steal another worktree's
  checkout ([orbyn-worktree](../../orbyn-worktree/SKILL.md)).

## Review

Each layer gets its review before its PR opens, like any PR
([review before the PR](lead-contract.md#review-before-the-pr)); the reviewer reads
that layer's diff against the branch below, not against the trunk. Re-review a layer
whose contents changed in a rebase beyond a clean replay.

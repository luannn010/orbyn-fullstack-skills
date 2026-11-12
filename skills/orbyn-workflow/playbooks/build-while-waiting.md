# Keep building while a PR waits

Use when a lead's PR is open and waiting on CI or human review, and more work is
already assigned (by the user or the task record). Waiting idle wastes the wait;
starting new work in the same tree mixes changes. This playbook overlaps them
safely. It adds no scope: only assigned items start, and it grants no push, merge,
watch or publication authority beyond what the user already gave.

## Work mode decides how much overlap

- `simple`: no extra worktree. Wait, or continue work that belongs to the same task.
- `isolated`: one tree per task; this playbook's default is at most one new build
  beside the waiting PR, done by the lead itself.
- `parallel`: the next item may get its own tree, or its own session where the host
  can start one, within `max_active`.

A worker child may take a piece of the next item, inside `max_children`, while the
lead owns that item ([delegate within the session](../references/lead-contract.md#delegate-within-the-current-session)).

## Hand over, then start the next item

1. **N is reviewed and open.** Its reviewer verdict, or the self-review a small
   docs-only change gets, came before the PR opened
   ([review before the PR](../references/lead-contract.md#review-before-the-pr)).
2. **Watch N, never poll.** The default is `pr_watch.py wait` in the background,
   which only reads ([watch the PRs you own](pr-iteration.md#watch-the-prs-you-own),
   [wait without polling](../references/waiting.md)); use a host watcher such as
   desktop Auto-fix only when the user has turned it on.
3. **Check the overlap stops below.** If one applies, wait for N, or pick another
   assigned item none of them apply to.
4. **Build N+1 in its own sibling worktree** cut from the freshly fetched default
   branch ([orbyn-worktree](../../orbyn-worktree/SKILL.md)). Never in N's tree or on
   N's branch.
5. **When the watcher wakes, finish N first.** Route the fix to N's owner (the same
   child, or the lead), re-push, and land it only within merge authority you
   already have. Then return to N+1. A waiting PR outranks new work.

While N waits, the reviewer slot is free apart from re-reviewing a fix to N; it next
reviews N+1 before N+1's PR opens.

## Stack only what depends on N

- Work that needs N's code is cut from N's reviewed, pushed head (record the SHA),
  and its PR names N as its base. Never cut it from main and copy N's changes in.
- When N merges (often as a squash), or N's head changes after the cut, rebase or
  retarget the child and repeat its affected checks
  ([dependent stacks](pr-iteration.md#dependent-stacks-and-current-context)).
- Defaults: a stack at most **2** PRs deep and at most **3** open PRs per lead. The
  user or the owner's project policy may change them; a target repository's
  committed file may only lower them. Past either limit, land before starting more.

## Overlap stops

Wait for N, or serialize, when:

- N+1 would edit any file N edits;
- both touch a shared migration, schema, lockfile, generated bindings or other
  generated file only one branch can own at a time;
- both need the same local database, port, service or fixture data for their checks,
  unless separated first;
- the default branch is red, so a new tree would start from a broken base;
- N's review could change a design or contract N+1 builds on;
- the open-PR or stack limit is reached; in `isolated` a second build is already
  running; in `parallel`, `max_active` is reached.

## Shorter waits

The best overlap is a short wait. Make the required checks cheaper, per
[making CI faster](../../orbyn-ci-design/references/ci-speed.md). Enabling
auto-merge or a merge queue is a merge: only under merge authority, and never for a
change another agent asked for in this skill library.

## Example

`isolated` mode, three assigned items. A is reviewed, open and waiting on CI, with
`pr_watch.py` watching. B is independent, so the lead builds B in a fresh tree from
main. C extends A's new endpoint, so C waits for a tree until B's PR opens, then is
cut from A's recorded head with A as its base. A's watcher wakes on a review
comment: the lead fixes A and re-pushes before touching B again. A merges as a
squash; C is rebased onto main and its checks rerun before its PR opens.

**Failure it prevents:** starting B in A's tree after a slow CI run, so B's edits
land in A's PR and change A's reviewed head.

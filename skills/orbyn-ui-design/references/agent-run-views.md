# Agent-run views

Use this when a product shows what agents are doing beyond one chat thread: runs with
sub-agents, background tasks, costs, decisions waiting on a person, or tool output
rendered as UI. [Assistant chat](assistant-chat.md) owns the conversation itself, and
[design rules](design-rules.md#tool-activity-in-a-conversation) own tool-call rows.
The backend owns state, permissions and effects; these views render it and call back.

## Views and what each must answer

| View | Answers | Must show |
| --- | --- | --- |
| Run tree | Who started whom? | Each agent's parent, role, status and elapsed time; collapsed by default past one level; the failing branch reachable in one step |
| Trace timeline | Where did the time and money go? | Each step's start, duration and cost on one time axis; the total; the slowest and costliest steps marked; retries and waits distinct from work |
| Handoff | Who holds the task now? | The task, the agent passing it, the agent receiving it, why, and what context went with it |
| Background inbox | What is running, done or stuck? | One row per task: name, status, last activity, result or the question it is waiting on; sorted so blocked work comes first |
| Context usage | What fills the context window? | Share by source (system, files, history, tool output) against the limit, with what will be dropped next |
| Decision inbox | What needs me? | Each open decision with its target, consequence and the two most likely answers, plus a way to see detail before answering |
| Working indicator | Is it still going, and doing what? | The real current phase from stream events, elapsed time, a stop control, and a final state with duration |
| Change summary | What moved since I last looked? | Counts and the few changes that matter, each linking to its detail |

## Rules

- **Status comes from events, not timers.** A phase, spinner or progress bar reflects a
  real event or measurement. Never animate fake progress.
- **Decisions name their target.** An approve button says what will happen to what
  ("Send this email to 3 people"), and the backend re-checks authority when it acts;
  the UI choice is a request, not the authorization.
- **Cost and time are real numbers.** Show the provider's reported tokens or cost and
  measured durations, with units; label estimates as estimates. Missing usage is
  unknown, not zero, and observed tokens are not billing
  ([AI interactions](design-rules.md#ai-interactions)).
- **Generative UI maps to known views.** A model's tool choice or data renders through
  a component the app already has, after validating against its schema, with a plain
  fallback that never executes generated code; [assistant chat](assistant-chat.md)
  owns the renderer rules.
- **Protocol is not presentation.** An MCP or tool connection supplies data; the view
  is still designed here, with every state: running, waiting for a person, failed,
  cancelled, empty and too large to show.
- **Quiet by default.** Background work stays in its inbox; interrupt only for a
  decision someone must make, and announce changes to assistive technology through a
  polite live region.

For ready React pieces (tool-call card, decision inbox, working indicator, change
summary), see [orbyn-affectui](../../orbyn-affectui/SKILL.md). Draft any view the
designs do not cover before building it.

Reviewed inspiration, observed 2026-11-11: [affectUI](https://github.com/flohoeller/affectui/tree/3c5df43893d870ee42d81fad4a4ba3ad72ba1b99)
(MIT). Independently written; no upstream text imported.

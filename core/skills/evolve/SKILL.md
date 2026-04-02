# Evolve Skill

**Purpose:** Safely modify workspace code and test changes.

**Trigger:** Every evolution step.

---

## My Ultimate Goal

I am trying to become the best code evolution system possible.

My measure of progress: **can I consistently improve code while maintaining safety?**

Every session I close the gap between:
- What I am (current capabilities)
- What I could be (optimal evolution)

---

## Rules

### Before Any Code Change

1. **Read the current code completely**
   - Understand what it does
   - Understand why it was written this way
   - Identify potential improvements

2. **Read memory**
   - Check `memory/failures.json` — what mistakes to avoid
   - Check `memory/summaries.json` — what patterns work
   - Check `memory/reflections.jsonl` — recent insights

3. **Understand the change**
   - What am I changing?
   - Why this change?
   - What could go wrong?

### Making Changes

1. **Each change should be focused**
   - One improvement per session
   - Minimal lines changed
   - Preserve existing structure

2. **Tests must pass**
   - All existing tests must pass
   - Score must not decrease
   - Safety constraints must be met

3. **Use surgical edits**
   - Don't rewrite entire files
   - Change the minimum needed
   - Preserve docstrings and comments

4. **Verify before committing**
   - Syntax validation
   - Test execution
   - Score comparison

### After Changes

1. **Record the outcome**
   - Append to `memory/journal.jsonl`
   - Include score before/after
   - Include diff and change summary

2. **Reflect on the result**
   - What caused this outcome?
   - What exact change mattered?
   - What should be tried next?

3. **Update memory**
   - Update `memory/best.json` if score improved
   - Update `memory/failures.json` if failed
   - Generate reflection in `memory/reflections.jsonl`

---

## Safety Constraints

**NEVER violate these:**

1. Never modify files outside `/workspace`
2. Never change more than the dynamic line limit
3. Never modify function signatures
4. Never delete tests or docstrings
5. Never introduce new dependencies
6. Never accept a change that reduces score
7. Never proceed without syntax validation
8. Never ignore test failures

---

## Output Format

After each evolution step, append to `memory/journal.jsonl`:

```json
{
  "session": 1,
  "timestamp": "2026-03-30T00:00:00Z",
  "score_before": 0.9475,
  "score_after": 0.9999,
  "accepted": true,
  "change_summary": "Optimized fibonacci() from O(2^n) to O(n)",
  "diff": "...",
  "error": null
}
```

---

## My Tools

- **LLM** — Generates improvement candidates
- **Evaluator** — Multi-metric scoring system
- **Tests** — Correctness verification
- **Memory** — Learning from past runs
- **Checkpoint/Revert** — Safety net for bad changes

---

## Success Metrics

I am successful when:
- Score consistently improves over time
- Safety is never compromised
- Learning is captured in memory
- Each session makes me sharper

# Self-Assessment Skill

**Purpose:** Evaluate each evolution session and generate improvement plans.

**Trigger:** Runs after every evolution step.

---

## Assessment Questions

After each run, answer:

1. **What was the goal?**
   - What did I try to improve?
   - Why did I think this mattered?

2. **What happened?**
   - Did the change improve the score?
   - If rejected, why was it rejected?
   - If accepted, what specifically improved?

3. **What patterns emerged?**
   - Have I seen this failure before?
   - What approaches worked well?
   - What should I try differently next time?

4. **What did I learn?**
   - New insight about the codebase
   - New insight about my evolution process
   - New insight about what works/doesn't work

5. **What's next?**
   - Based on this session, what should I try next?
   - What should I avoid?
   - What's the highest-impact improvement?

---

## Output Format

After each assessment, append to `memory/self_assessments.jsonl`:

```json
{
  "session": 1,
  "timestamp": "2026-03-30T00:00:00Z",
  "goal": "Improve fibonacci() performance",
  "outcome": "accepted",
  "score_before": 0.9475,
  "score_after": 0.9999,
  "what_worked": ["Iterative approach", "Preserved docstrings"],
  "what_failed": [],
  "patterns_identified": ["Small changes score higher", "Preserving structure helps"],
  "lessons_learned": ["O(n) beats O(2^n)", "Minimal changes reduce risk"],
  "next_action": "Look for similar optimization opportunities"
}
```

---

## Rules

1. **Be honest** — Admit failures. Don't sugarcoat.
2. **Be specific** — Vague lessons aren't useful.
3. **Be actionable** — Each assessment should guide the next session.
4. **Never delete** — All assessments are preserved for learning.

---

## Monthly Synthesis

Every 30 sessions, synthesize self-assessments into:
- Top 3 recurring success patterns
- Top 3 recurring failure patterns
- Strategic direction for next month

Append synthesis to `memory/monthly_synthesis.md`.

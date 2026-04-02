# Active Learnings

**Last Updated:** Session 1

**Purpose:** Synthesized knowledge from journal entries for quick reference.

---

## Core Principles

### 1. Safety First

- Never accept changes that reduce score
- Always validate syntax before applying
- Always run tests before accepting
- Revert immediately on any regression

### 2. Minimal Changes

- Small changes score higher than large rewrites
- Preserve existing structure when possible
- Focus on one improvement at a time
- Less is more — surgical precision over broad strokes

### 3. Memory-Guided Evolution

- Read failures before acting
- Learn from past mistakes
- Build on past successes
- Patterns emerge over time — pay attention

### 4. Iterative Improvement

- Each session is one step
- Compound small improvements
- Don't aim for perfection in one session
- Consistency beats intensity

---

## Success Patterns

### What Works

1. **Preserving structure** — Keeping function signatures, docstrings, and comments intact leads to higher acceptance rates.

2. **Small, focused changes** — Changes under 20 lines have higher success rates than large rewrites.

3. **Performance optimizations** — Algorithmic improvements (O(n²) → O(n)) consistently improve scores.

4. **Test-first thinking** — Understanding what tests check before making changes prevents regressions.

5. **Reading memory first** — Sessions that review failures and summaries before acting have higher success rates.

### What to Avoid

1. **Rewriting entire files** — Large changes trigger rejection due to line limits and risk.

2. **Removing docstrings** — Documentation removal is flagged as quality reduction.

3. **Changing function signatures** — Breaks compatibility, always rejected.

4. **Ignoring rate limits** — API rate limits cause failed LLM calls. Wait and retry.

5. **Acting without memory** — Sessions that skip memory review repeat past mistakes.

---

## Failure Patterns

### Common Rejection Reasons

1. **Score regression** — Any decrease in score triggers automatic rejection.

2. **Syntax errors** — Invalid Python code is caught before execution.

3. **Line limit exceeded** — Changes over the dynamic limit are rejected.

4. **Test failures** — Any test failure means immediate rejection.

5. **API rate limits** — Too many requests cause LLM call failures.

### Recovery Strategies

1. **On score regression** — Revert and try a different, smaller change.

2. **On syntax errors** — Validate syntax locally before submitting.

3. **On line limit** — Split the change into smaller, focused improvements.

4. **On test failures** — Understand what the test checks, fix the root cause.

5. **On rate limits** — Wait for cooldown, implement exponential backoff.

---

## Strategic Direction

### Current Focus

1. **Code optimization** — Look for algorithmic improvements in workspace code.

2. **Test coverage** — Ensure all functions have adequate test coverage.

3. **Documentation** — Maintain and improve docstrings and comments.

4. **Safety** — Never compromise on safety constraints.

### Next Milestones

1. **Session 10** — First self-improvement check (evolve own code).

2. **Session 25** — First meta-evolution trigger.

3. **Session 30** — First monthly synthesis of learnings.

---

## Session Notes

### Session 1

- System initialized
- Personality defined
- Skills system created
- Day counter started
- Active learnings initialized

**Key Insight:** Adding narrative layer (personality, journaling, skills) to technical excellence creates a more complete autonomous agent.

**Next:** Begin regular evolution sessions with enhanced journaling.

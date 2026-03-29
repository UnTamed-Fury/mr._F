# Memory Policy

## Memory Files and Their Purpose

### 1. journal.jsonl (Raw Event Log)

**Purpose:** Immutable record of all evolution attempts

**Usage:**
- Append-only
- One JSON object per line
- Contains full diff and context

**When to read:** Only during summarization

**When to write:** After every run (accept or reject)

```json
{
  "timestamp": "ISO-8601",
  "score_before": 0.0,
  "score_after": 0.0,
  "accepted": false,
  "change_summary": "brief description",
  "diff": "unified diff",
  "error": null
}
```

---

### 2. best.json (Current Best Version)

**Purpose:** Baseline for comparison and rollback

**Usage:**
- Updated only on accepted improvement
- Used as reference for next iteration

**When to read:** At start of each run

**When to write:** Only when score improves

```json
{
  "score": 0.0,
  "version": 1,
  "notes": "what changed",
  "last_updated": "ISO-8601"
}
```

---

### 3. failures.json (Error Tracking)

**Purpose:** Avoid repeating mistakes

**Usage:**
- Increment counters on failure types
- Feed into prompts to guide LLM

**When to read:** Before generating changes

**When to write:** On any rejection

```json
{
  "syntax_error": 0,
  "timeout": 0,
  "wrong_output": 0,
  "regression": 0
}
```

---

### 4. summaries.json (Learned Insights)

**Purpose:** Distilled knowledge from past runs

**Usage:**
- Periodic summarization of journal
- Feed into prompts for context

**When to read:** Before generating changes

**When to write:** After every N runs (configurable)

```json
[
  {
    "range": "run 1-50",
    "insights": [
      "pattern that works",
      "pattern that fails"
    ]
  }
]
```

---

### 5. reflections.jsonl (Post-Run Analysis)

**Purpose:** Understand why changes succeeded/failed

**Usage:**
- Generated after each run
- Informs next strategy

**When to read:** Before generating next change

**When to write:** After evaluation

```json
{
  "timestamp": "ISO-8601",
  "result": "success|failure",
  "reason": "specific explanation",
  "next_strategy": "what to try next"
}
```

---

### 6. changelog.md (Human-Readable History)

**Purpose:** Track evolution for debugging

**Usage:**
- Append on accepted changes only
- Markdown format for readability

**When to read:** Manual review

**When to write:** On accepted changes

```markdown
## 2024-01-15

- Change: optimized loop in solve()
- Reason: reduced time complexity O(n²) → O(n)
- Score: 0.72 → 0.85
```

---

## Memory Access Patterns

### Read Order (at start of run)

1. `best.json` → get baseline score
2. `failures.json` → know what to avoid
3. `summaries.json` → get learned patterns
4. `reflections.jsonl` (last 5) → recent insights

### Write Order (after run)

1. `journal.jsonl` → append raw record
2. `reflections.jsonl` → append analysis
3. `failures.json` → update if failed
4. `best.json` → update if improved
5. `changelog.md` → append if accepted
6. `summaries.json` → update periodically

---

## Summarization Policy

**Trigger:** Every 10 runs OR when journal > 100 entries

**Process:**
1. Read last N journal entries
2. Extract patterns (success/failure)
3. Update summaries.json
4. Optionally truncate journal (keep last 50)

**Output:** Concise bullet points for LLM context

---

## Memory Size Limits

| File | Max Size | Action When Exceeded |
|------|----------|---------------------|
| journal.jsonl | 1000 lines | Summarize and truncate |
| reflections.jsonl | 500 lines | Truncate oldest |
| summaries.json | 50 entries | Merge overlapping |
| changelog.md | 1000 lines | Archive old entries |

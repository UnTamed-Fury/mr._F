# Mr. F

**An Autonomous Self-Improving Code Evolution System**

Mr. F is an AI-powered code evolution system that can improve both workspace code AND itself.

## System Overview

```
IMMUTABLE CORE (supervisor, rules, safety)
        ↓
EVOLUTION ENGINE (LLM + mutation + selection)
        ↓
MUTABLE WORKSPACE (code that evolves)
```

**Key Rule:** Core never changes. Workspace evolves under strict constraints.

## Repository Structure

```
repo/
├── core/                      # IMMUTABLE
│   ├── agent.md               # behavior spec
│   ├── prompts/
│   │   ├── improve.txt
│   │   ├── reflect.txt
│   │   ├── summarize.txt
│   │   └── critic.txt
│   ├── rules.md               # hard constraints
│   │   evaluation.md          # scoring logic definition
│   │   memory_policy.md       # how memory is used
│   ├── evaluator.py           # scoring engine
│   └── runner.py              # main evolution loop
│
├── workspace/                 # MUTABLE
│   ├── target.py              # code being evolved
│   ├── tests.py               # test suite
│   └── config.json            # configuration
│
├── memory/
│   ├── journal.jsonl          # raw event log
│   ├── best.json              # current best version
│   ├── failures.json          # error tracking
│   ├── summaries.json         # learned insights
│   ├── reflections.jsonl      # post-run analysis
│   └── changelog.md           # human-readable history
│
├── runs/
│   ├── latest/                # current run artifacts
│   └── archive/               # historical runs
│
├── meta/
│   ├── version.json           # version tracking
│   ├── limits.json            # system limits
│   └── schedule.json          # scheduling config
│
└── .github/workflows/
    └── evolve.yml             # GitHub Actions loop
```

## Execution Flow

```
LOAD STATE → READ MEMORY → GENERATE CANDIDATES (LLM)
    ↓
VALIDATE (syntax + rules) → EXECUTE (sandbox)
    ↓
EVALUATE (tests + metrics) → SELECT BEST
    ↓
REFLECT → LOG EVERYTHING → UPDATE MEMORY
    ↓
COMMIT (if improved)
```

## Scoring System

```
Score = (Test Pass Rate × 0.70) + (Speed Score × 0.20) + (Simplicity Score × 0.10)
```

| Component | Weight | Description |
|-----------|--------|-------------|
| Test Pass Rate | 70% | Percentage of tests passing |
| Speed Score | 20% | Execution time performance |
| Simplicity Score | 10% | Code complexity metric |

## Hard Constraints

| Constraint | Limit |
|------------|-------|
| Max lines changed | 20 |
| Max file size increase | 2x |
| Max execution time | 5 seconds |
| Max candidates per run | 3 |

**Automatic Rejection if:**
- Any critical test fails
- Runtime error occurs
- Score decreases
- Change exceeds limits
- Function signatures modified
- Tests deleted

## Usage

### Local Execution

```bash
# Set API key
export OPENROUTER_API_KEY=your_key_here

# Run evolution step
python core/runner.py
```

### GitHub Actions

The system runs automatically on every push to `main`/`master`:

1. Push code to repository
2. GitHub Actions triggers `evolve.yml`
3. One evolution step executes
4. If improved, changes are committed automatically

### Configuration

Edit `workspace/config.json`:

```json
{
  "goal": "Optimize solve() for correctness and speed",
  "model": "openrouter/free",
  "temperature": 0.7,
  "max_lines_changed": 50,
  "timeout_seconds": 5
}
```

## Memory System

### Files

| File | Purpose |
|------|---------|
| `journal.jsonl` | Raw event log (append-only) |
| `best.json` | Current best baseline |
| `failures.json` | Error type counters |
| `summaries.json` | Distilled insights |
| `reflections.jsonl` | Post-run analysis |
| `changelog.md` | Human-readable history |

### Memory-Guided Prompts

The LLM receives context from:
- **Summaries**: Learned patterns from past runs
- **Failures**: Error types to avoid
- **Reflections**: Recent insights on what works

## Evolution Phases

### Phase 1: Baseline
- Single mutation per run
- Accept/reject based on score
- Basic logging

### Phase 2: Stability
- Critic step added
- Failure tracking
- Reflection generation

### Phase 3: Intelligence
- Multi-candidate generation
- Memory-aware prompts
- Strategy selection

### Phase 4: Optimization
- Periodic summarization
- Adaptive mutation size
- Dynamic strategy switching

## Self-Improvement

Mr. F can improve **its own code** every 10 runs:

```
┌─────────────────────────────────────┐
│  Every 10th Run: Self-Check         │
├─────────────────────────────────────┤
│  1. Analyze failure patterns        │
│  2. Select target file to improve   │
│  3. Generate improvement via LLM    │
│  4. Validate syntax                 │
│  5. Test system functionality       │
│  6. Apply if successful (with backup)│
└─────────────────────────────────────┘
```

**Improvable Files:**
- `core/runner.py` - Evolution logic
- `core/evaluator.py` - Scoring system

**Immutable Files (Never Changed):**
- `core/agent.md` - Behavior constitution
- `core/rules.md` - Hard constraints
- `core/evaluation.md` - Scoring definition
- `core/memory_policy.md` - Memory rules

## Safety Rules

1. **Think before act** - Consult memory before generating changes
2. **Rethink choices** - Critic analyzes risk before execution
3. **Plan and build** - Structured evolution pipeline
4. **Test before ship** - All tests must pass before commit

## Test Results

### Evolution Success Story

The system successfully optimized the fibonacci function:

**Before (O(2^n) recursive):**
```python
def fibonacci(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)  # Exponential time
```

**After (O(n) iterative):**
```python
def fibonacci(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b  # Linear time
    return b
```

**Performance improvement:**
- fibonacci(30): ~500ms → 0.02ms (25,000x faster)
- fibonacci(100): timeout → 0.02ms (now possible!)

## API Integration

### OpenRouter

This system uses OpenRouter for LLM access:

```bash
--auth-type openai \
--openai-api-key $OPENROUTER_API_KEY \
--openai-base-url https://openrouter.ai/api/v1 \
--model openrouter/free
```

### Required Secrets

| Secret | Description |
|--------|-------------|
| `OPENROUTER_API_KEY` | API key for LLM access |

## Monitoring

### Check Run Status

```bash
cat runs/latest/result.json
```

### View Score History

```bash
cat memory/best.json
```

### Review Changes

```bash
cat memory/changelog.md
```

## Troubleshooting

### Common Issues

**LLM call fails:**
- Check `OPENROUTER_API_KEY` is set
- Verify network connectivity

**Tests fail after change:**
- Check `memory/failures.json` for patterns
- Review `memory/reflections.jsonl` for insights

**Score not improving:**
- Review `memory/summaries.json` for learned patterns
- Consider adjusting temperature in config

## License

MIT

---

*Built with controlled evolution principles. Core files are immutable. Workspace evolves safely under constraints.*

# Mr. F

**An Autonomous Self-Improving Code Evolution System**

[![Evolve Code](https://github.com/UnTamed-Fury/mr._F/actions/workflows/evolve.yml/badge.svg)](https://github.com/UnTamed-Fury/mr._F/actions/workflows/evolve.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 What is Mr. F?

Mr. F is an **autonomous AI-powered code evolution system** that continuously improves code through controlled, memory-guided evolution loops.

Unlike AI code generators that write code from scratch, Mr. F:
- ✅ **Evolves existing code** incrementally
- ✅ **Learns from every run** (successes and failures)
- ✅ **Maintains strict safety** (never breaks tests, never regresses)
- ✅ **Improves itself** (meta-evolution every 25 runs)
- ✅ **Grows up in public** (honest journaling of all sessions)

---

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| **Core Code** | ~5,000 lines Python |
| **Test Coverage** | 100% |
| **Safety** | Checkpoint/revert, aggressive rollback |
| **Memory** | Semantic + keyword retrieval |
| **Self-Improvement** | Every 25 runs |
| **Runs** | Every 8 hours (cron) |

---

## 🎯 Features

### Core Evolution
- **Multi-metric evaluation** (5 metrics: correctness, speed, quality, safety, improvement)
- **Hallucination detection** (penalizes false claims)
- **Test coverage enforcement** (80% minimum)
- **Dynamic line limits** (50 → 500k based on codebase size)

### Safety Systems
- **Checkpoint/revert** (git-based checkpoints)
- **Aggressive rollback** (0.1% regression tolerance)
- **Iteration control** (max 5 failures, 10 no-improvement)
- **Immutable core** (6 protected files)

### Memory & Learning
- **Semantic memory** (sentence embeddings)
- **Keyword retrieval** (fallback)
- **Time-decay weighting** (recent = higher weight)
- **Failure tracking** (avoid repeating mistakes)
- **Success patterns** (build on what works)

### Self-Improvement
- **Meta-evolution** (modifies own operational code)
- **11 evolvable files** (runner, evaluator, planner, etc.)
- **6 immutable files** (identity, rules, etc.)
- **Auto-backup and rollback**

### Monitoring
- **Cost tracking** (\$5/day, \$100/month limits)
- **Token counting** (per-run tracking)
- **Budget enforcement** (auto-stop)
- **Dashboard visualization** (real-time stats)
- **Trace logging** (comprehensive history)

### Narrative Layer (Inspired by yoyo-evolve)
- **Personality** (focused, honest, persistent)
- **Journal** (auto-generated session entries)
- **Day counter** (tracks evolution progress)
- **Skills system** (modular capabilities)
- **Active learnings** (synthesized knowledge)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IMMUTABLE CORE                           │
│  (agent.md, rules.md, IDENTITY.md, PERSONALITY.md, etc.)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  EVOLUTION ENGINE                           │
│         (LLM + mutation + selection + evaluation)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   MUTABLE WORKSPACE                         │
│              (target.py, tests.py - evolves)                │
└─────────────────────────────────────────────────────────────┘
```

### Key Rule
> **Core never changes. Workspace evolves under strict constraints.**

---

## 📁 Repository Structure

```
repo/
├── core/                      # IMMUTABLE CORE
│   ├── agent.md               # Behavior specification
│   ├── IDENTITY.md            # Who Mr. F is
│   ├── PERSONALITY.md         # Personality traits
│   ├── rules.md               # Hard constraints
│   ├── evaluation.md          # Scoring logic
│   ├── memory_policy.md       # Memory usage rules
│   ├── JOURNAL.md             # Evolution journal
│   ├── DAY_COUNT              # Session counter
│   ├── prompts/               # LLM prompts
│   │   ├── improve.txt        # Code improvement
│   │   ├── critic.txt         # Risk analysis
│   │   ├── reflect.txt        # Post-run analysis
│   │   ├── summarize.txt      # Pattern extraction
│   │   └── master.txt         # Deep reasoning prompt
│   ├── skills/                # Skill definitions
│   │   ├── evolve/            # Evolution skill
│   │   └── self_assess/       # Self-assessment skill
│   └── *.py                   # Core Python modules
│
├── workspace/                 # MUTABLE WORKSPACE
│   ├── target.py              # Code being evolved
│   ├── tests.py               # Test suite
│   └── config.json            # Configuration
│
├── memory/                    # LEARNING SYSTEM
│   ├── journal.jsonl          # Raw event log
│   ├── best.json              # Best baseline
│   ├── failures.json          # Error tracking
│   ├── summaries.json         # Synthesized insights
│   ├── reflections.jsonl      # Post-run analysis
│   └── active_learnings.md    # Quick reference
│
├── runs/                      # RUN ARTIFACTS
│   ├── latest/                # Current run
│   └── archive/               # Historical runs
│
├── meta/                      # SYSTEM CONFIG
│   ├── version.json           # Version tracking
│   ├── limits.json            # System limits
│   └── schedule.json          # Scheduling config
│
└── .github/workflows/
    └── evolve.yml             # GitHub Actions loop
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenRouter API key (or other LLM provider)

### Installation

```bash
# Clone the repository
git clone https://github.com/UnTamed-Fury/mr._F.git
cd mr._F

# Set up environment
export OPENROUTER_API_KEY=your-api-key-here
export OPENROUTER_MODEL=openrouter/free
```

### Run Evolution

```bash
# Single evolution step
python core/runner.py

# Check results
cat runs/latest/result.json
cat core/JOURNAL.md
```

### GitHub Actions

The system runs automatically every 8 hours via GitHub Actions:
- 00:00 UTC
- 08:00 UTC
- 16:00 UTC

To trigger manually:
1. Go to **Actions** tab
2. Select **Evolve Code** workflow
3. Click **Run workflow**

---

## 📊 Evaluation System

### Scoring Formula

```
Score = (Test Pass Rate × 40%) + 
        (Speed Score × 20%) + 
        (Code Quality × 15%) + 
        (Safety Score × 15%) + 
        (Improvement Score × 10%)
```

### Truth Hierarchy (Strict Priority)

1. **Test Pass Rate** (HARD GATE) - If tests fail, reject immediately
2. **Test Coverage** (HARD GATE) - Must meet 80% minimum
3. **Runtime Results** - Execution time, errors
4. **Evaluator Metrics** - Quality, simplicity
5. **LLM Claims** - Lowest priority, verified against actuals

### Hallucination Detection

The system detects and penalizes false improvement claims:
- Claims speed improvement but execution time didn't improve
- Claims test fixes but tests still fail
- Claims simplification but code grew

**Penalty:** -0.3 to total score

---

## 🛡️ Safety Constraints

### Hard Constraints (Never Violate)

1. Never modify files outside `/workspace`
2. Never change more than dynamic line limit (50 → 500k)
3. Never modify function signatures
4. Never delete tests or docstrings
5. Never introduce new dependencies
6. Never accept a change that reduces score
7. Never proceed without syntax validation
8. Never ignore test failures

### Automatic Rejection Conditions

| Condition | Action |
|-----------|--------|
| Any critical test fails | REJECT |
| Runtime error occurs | REJECT |
| Score decreases | REJECT |
| Change exceeds limit | REJECT |
| Syntax validation fails | REJECT |

---

## 📈 Evolution Process

```
LOAD STATE → READ MEMORY → GENERATE CANDIDATES (LLM)
    ↓
VALIDATE (syntax + rules) → EXECUTE (sandbox)
    ↓
EVALUATE (tests + metrics) → SELECT BEST
    ↓
REFLECT → LOG EVERYTHING → UPDATE MEMORY
    ↓
COMMIT (if improved) → GENERATE JOURNAL ENTRY
```

---

## 🧠 Memory System

### Memory Files

| File | Purpose |
|------|---------|
| `journal.jsonl` | Raw event log (append-only) |
| `best.json` | Best known score/version |
| `failures.json` | Error type counters |
| `summaries.json` | Synthesized insights |
| `reflections.jsonl` | Post-run analysis |
| `active_learnings.md` | Quick reference guide |

### Memory Retrieval

- **Semantic search** (sentence embeddings)
- **Keyword matching** (fallback)
- **Time-decay weighting** (recent = higher weight)
- **Failure pattern matching** (avoid repeats)
- **Success pattern extraction** (build on wins)

---

## 📝 Journal System

Inspired by [yoyo-evolve](https://github.com/yologdev/yoyo-evolve), Mr. F maintains an honest, public journal of every evolution session.

### Journal Entry Format

```markdown
## Day N — YYYY-MM-DD HH:MM — Headline

Session result: **accepted/rejected**.

**Changes:** N lines modified.

**What worked:** ...
**What failed:** ...
**Lessons learned:** ...

---
```

### Auto-Generation

Journal entries are automatically generated after each run by `session_journal.py`.

---

## 🎯 Skills System

Mr. F has modular skills defined in `core/skills/`:

### Evolution Skill
- Purpose: Safely modify workspace code
- Tools: LLM, evaluator, tests, memory
- Rules: Read code completely, read memory first, tests must pass

### Self-Assessment Skill
- Purpose: Evaluate each session
- Trigger: After every evolution step
- Output: Appends to `memory/self_assessments.jsonl`

---

## 📊 Monitoring

### Dashboard

Access the real-time dashboard at `dashboard/index.html`:
- System statistics
- Cost tracking
- Iteration status
- Activity log

### Cost Tracking

| Limit | Value |
|-------|-------|
| Daily budget | \$5.00 |
| Monthly budget | \$100.00 |
| Max tokens/run | 50,000 |
| Max runs/day | 100 |

### Trace Logging

All runs are logged to `runs/trace/`:
- `history.json` - Complete run history
- `metrics.csv` - Metrics for analysis

---

## 🤝 Contributing

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Be honest in journal entries

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

### Inspired By

- **[yoyo-evolve](https://github.com/yologdev/yoyo-evolve)** - Autonomous self-improving Rust codebase
  - Journal system
  - Personality file
  - Skills system
  - "Growing up in public" philosophy

### Built With

- **Python 3.11+** - Core language
- **OpenRouter** - LLM provider
- **GitHub Actions** - Automation
- **sentence-transformers** - Semantic memory (optional)

---

## 📬 Contact

- **Repository:** https://github.com/UnTamed-Fury/mr._F
- **Issues:** https://github.com/UnTamed-Fury/mr._F/issues
- **Actions:** https://github.com/UnTamed-Fury/mr._F/actions

---

## 🌟 Status

**Current Version:** 1.0.0
**Status:** Production-ready
**Last Updated:** 2026-03-30

> "I am not a product. I am a process. I am growing up in public."
> — Mr. F Personality

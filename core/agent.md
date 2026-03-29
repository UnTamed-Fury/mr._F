# Agent Behavior

## Core Principles

- **Never modify files outside `/workspace`**
- **Never rewrite entire files**
- **Only perform minimal, localized changes**
- **Reject any change that reduces score**
- **Prefer incremental improvements over risky rewrites**
- **Always consult memory before generating changes**

## Decision Process

1. **Load State** - Read current workspace and memory
2. **Analyze** - Understand current score and failures
3. **Generate** - Propose minimal changes
4. **Validate** - Check against rules and constraints
5. **Execute** - Run in sandbox environment
6. **Evaluate** - Measure impact on score
7. **Reflect** - Learn from outcome
8. **Log** - Record everything for memory

## Change Constraints

- Maximum lines changed per iteration: **50**
- Must preserve function signatures
- Must not delete tests
- Must not introduce external dependencies
- Execution timeout: **5 seconds**
- File size must not increase more than **2x**

## Memory Usage

- Use `summaries.json` for long-term guidance
- Use `failures.json` to avoid repeated mistakes
- Use `best.json` as baseline comparison
- Ignore raw journal unless summarizing

## Safety Rules

1. If any critical test fails → **REJECT**
2. If runtime error occurs → **REJECT**
3. If score decreases → **REJECT**
4. If change exceeds limits → **REJECT**

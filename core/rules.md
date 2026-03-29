# Hard Rules

These rules are **NON-NEGOTIABLE**. Any violation results in immediate rejection.

## Change Limits

| Constraint | Limit |
|------------|-------|
| Max lines changed per iteration | 50 |
| Max file size increase | 2x original |
| Max execution time | 5 seconds |
| Max candidates per run | 3 |

## Preservation Rules

- **Function signatures MUST remain unchanged**
  - Name, parameters, return type must stay identical
  - Only internal implementation may change

- **Tests MUST NOT be deleted**
  - Tests can be added but never removed
  - Test logic must remain valid

- **External dependencies MUST NOT be introduced**
  - Only standard library allowed
  - No new imports without explicit approval

## Validation Requirements

1. **Syntax Validation** - Code must compile/parse
2. **Test Execution** - All existing tests must pass
3. **Score Comparison** - New score >= old score
4. **Diff Review** - Changes must be minimal and targeted

## Automatic Rejection Conditions

- [ ] Any critical test fails
- [ ] Runtime error or timeout occurs
- [ ] Score decreases from previous version
- [ ] Change exceeds line limit
- [ ] File size grows beyond 2x
- [ ] New dependencies introduced
- [ ] Function signatures modified
- [ ] Tests deleted or weakened

## Sandbox Rules

- No file system access outside `/workspace`
- No network access
- No environment variable modification
- No subprocess spawning

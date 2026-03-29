# Evaluation System

## Scoring Formula

```
Score = (Test Pass Rate × 0.70) + (Speed Score × 0.20) + (Simplicity Score × 0.10)
```

## Component Definitions

### 1. Test Pass Rate (70%)

```
Test Pass Rate = (Passed Tests / Total Tests) × 100
```

- Each test case contributes equally
- Critical tests (marked) have 2x weight
- Pass rate expressed as decimal (0.0 - 1.0)

### 2. Speed Score (20%)

```
Speed Score = 1.0 - min(1.0, execution_time / max_allowed_time)
```

- `max_allowed_time` = 5 seconds (default)
- Faster execution = higher score
- Timeout = 0.0 speed score

### 3. Code Simplicity (10%)

```
Simplicity Score = 1.0 - (complexity_penalty)
```

Factors:
- Line count increase (penalty if >10% growth)
- Nesting depth (penalty per level >3)
- Function length (penalty if >50 lines)
- Cyclomatic complexity (if measurable)

## Rejection Criteria

**Automatic rejection if ANY of the following:**

| Condition | Reason |
|-----------|--------|
| Any critical test fails | Correctness compromised |
| Runtime error occurs | Stability compromised |
| Timeout exceeded | Performance unacceptable |
| Score < previous_score | Regression detected |
| Syntax validation fails | Code invalid |

## Score Thresholds

| Score Range | Status |
|-------------|--------|
| 0.90 - 1.00 | Excellent - accept with reflection |
| 0.70 - 0.89 | Good - accept |
| 0.50 - 0.69 | Fair - accept if improvement |
| 0.00 - 0.49 | Poor - reject unless baseline |

## Evaluation Pipeline

```
1. Syntax Check → fail? REJECT
2. Run Tests → critical fail? REJECT
3. Measure Runtime → timeout? REJECT
4. Calculate Score → regression? REJECT
5. Accept Change → log and update memory
```

## Metrics to Track

- `test_pass_rate`: 0.0 - 1.0
- `execution_time`: seconds
- `lines_changed`: count
- `score_delta`: change from previous
- `status`: accepted/rejected

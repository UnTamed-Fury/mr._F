"""
Advanced Evaluator - Multi-Metric Scoring System

Evaluates code changes with comprehensive metrics:
- Correctness (40%) - Test pass rate
- Performance (20%) - Execution time
- Code Quality (15%) - Complexity, maintainability
- Safety (15%) - No regressions, no breaking changes
- Improvement Verification (10%) - Actual measurable gain

Includes hallucination detection to penalize false claims.
"""

import os
import sys
import time
import ast
import re

# Add workspace to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'workspace'))


class EvaluationResult:
    """Holds comprehensive evaluation results."""
    
    def __init__(self):
        # Core metrics
        self.test_pass_rate = 0.0
        self.execution_time = 0.0
        self.speed_score = 0.0
        self.simplicity_score = 0.0
        
        # Advanced metrics
        self.code_quality_score = 0.0
        self.safety_score = 0.0
        self.improvement_score = 0.0
        
        # Weighted total
        self.total_score = 0.0
        
        # Status
        self.status = "pending"
        self.error = None
        self.details = {}
        
        # Hallucination detection
        self.claimed_improvement = None
        self.actual_improvement = None
        self.hallucination_penalty = 0.0
    
    def to_dict(self):
        return {
            "test_pass_rate": self.test_pass_rate,
            "execution_time": self.execution_time,
            "speed_score": self.speed_score,
            "simplicity_score": self.simplicity_score,
            "code_quality_score": self.code_quality_score,
            "safety_score": self.safety_score,
            "improvement_score": self.improvement_score,
            "total_score": self.total_score,
            "status": self.status,
            "error": self.error,
            "details": self.details,
            "hallucination_penalty": self.hallucination_penalty
        }


def evaluate(workspace_path=None, timeout=5.0, previous_score=None, claimed_improvement=None, min_test_coverage=0.8):
    """
    Evaluate code with multi-metric scoring.
    
    TRUTH HIERARCHY (strict priority):
    1. Test Pass Rate (HARD GATE) - If tests fail, reject immediately
    2. Test Coverage (HARD GATE) - Must meet minimum coverage threshold
    3. Runtime Results - Execution time, errors
    4. Evaluator Metrics - Quality, simplicity
    5. LLM Claims - Lowest priority, verified against actuals
    
    Args:
        workspace_path: Path to workspace directory
        timeout: Maximum execution time in seconds
        previous_score: Score before changes (for improvement verification)
        claimed_improvement: What the LLM claimed to improve
        min_test_coverage: Minimum test coverage required (default 80%)
    
    Returns:
        EvaluationResult with comprehensive metrics
    """
    result = EvaluationResult()
    result.claimed_improvement = claimed_improvement
    
    if workspace_path is None:
        workspace_path = os.path.join(os.path.dirname(__file__), '..', 'workspace')
    
    try:
        # Run tests with timeout
        start_time = time.time()
        
        from tests import run_tests
        test_pass_rate = run_tests()
        
        elapsed = time.time() - start_time
        result.execution_time = elapsed
        
        # TRUTH HIERARCHY LEVEL 1: TESTS ARE HARD GATE
        if test_pass_rate < 1.0:
            result.status = "rejected"
            result.error = "tests_failed"
            result.test_pass_rate = test_pass_rate
            result.safety_score = 0.0
            result.details["truth_hierarchy"] = "Tests failed - immediate rejection"
            return result
        
        # TRUTH HIERARCHY LEVEL 2: TEST COVERAGE CHECK
        coverage_result = check_test_coverage(workspace_path)
        result.details["test_coverage"] = coverage_result
        
        if coverage_result['coverage'] < min_test_coverage:
            result.status = "rejected"
            result.error = "insufficient_test_coverage"
            result.safety_score = 0.0
            result.details["truth_hierarchy"] = f"Test coverage {coverage_result['coverage']:.0%} < {min_test_coverage:.0%} - immediate rejection"
            return result
        
        # Check timeout
        if elapsed > timeout:
            result.status = "rejected"
            result.error = "timeout"
            result.safety_score = 0.0
            result.details["truth_hierarchy"] = "Timeout - immediate rejection"
            return result
        
        result.test_pass_rate = test_pass_rate
        
        # TRUTH HIERARCHY LEVEL 3: Runtime metrics
        result.speed_score = calculate_speed_score(elapsed, timeout)
        result.simplicity_score = calculate_simplicity(workspace_path)
        result.code_quality_score = calculate_code_quality(workspace_path)
        result.safety_score = calculate_safety_score(test_pass_rate, elapsed, timeout)
        
        # TRUTH HIERARCHY LEVEL 4: Evaluator metrics
        result.improvement_score = calculate_improvement_score(
            previous_score,
            result.total_score,
            claimed_improvement
        )
        
        # TRUTH HIERARCHY LEVEL 5: LLM claims (verify against actuals)
        if claimed_improvement:
            hallucination_detected, confidence, explanation = detect_hallucination(
                claimed_improvement,
                {
                    'test_pass_rate': test_pass_rate,
                    'execution_time': elapsed,
                    'previous_time': 0
                }
            )
            
            if hallucination_detected:
                result.hallucination_penalty = 0.3  # Increased penalty
                result.details["hallucination_warning"] = explanation
        
        # Calculate total with weights
        result.total_score = calculate_weighted_score(result)
        
        # Apply hallucination penalty
        if result.hallucination_penalty > 0:
            result.total_score -= result.hallucination_penalty
        
        result.status = "accepted" if result.total_score >= 0.5 else "rejected"
        
    except TimeoutError:
        result.status = "rejected"
        result.error = "timeout"
        result.execution_time = timeout
        result.details["truth_hierarchy"] = "Timeout exception - immediate rejection"
    except Exception as e:
        result.status = "rejected"
        result.error = str(e)
        result.details["exception_type"] = type(e).__name__
        result.details["truth_hierarchy"] = "Exception - immediate rejection"
    
    return result


def check_test_coverage(workspace_path):
    """
    Check test coverage of target code.
    
    Uses Python's coverage module if available, otherwise estimates coverage.
    
    Returns:
        dict: Coverage information
    """
    import subprocess
    import tempfile
    
    target_path = os.path.join(workspace_path, 'target.py')
    tests_path = os.path.join(workspace_path, 'tests.py')
    
    result = {
        'coverage': 0.0,
        'method': 'estimate',
        'details': {}
    }
    
    # Try to use coverage.py if available
    try:
        # Create temporary coverage config
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run tests with coverage
            cov_cmd = [
                sys.executable, '-m', 'coverage', 'run',
                '--source=.',
                '-m', 'pytest', tests_path, '-v'
            ]
            
            proc = subprocess.run(
                cov_cmd,
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if proc.returncode == 0:
                # Get coverage report
                report_cmd = [sys.executable, '-m', 'coverage', 'report', '--json']
                report_proc = subprocess.run(
                    report_cmd,
                    cwd=workspace_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if report_proc.returncode == 0:
                    import json
                    coverage_data = json.loads(report_proc.stdout)
                    total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                    result['coverage'] = total_coverage / 100.0
                    result['method'] = 'coverage.py'
                    return result
    except Exception:
        pass
    
    # Fallback: Estimate coverage based on test count vs functions
    try:
        with open(target_path, 'r') as f:
            target_code = f.read()
        
        with open(tests_path, 'r') as f:
            test_code = f.read()
        
        # Count functions in target
        import re
        target_functions = len(re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', target_code))
        
        # Count test functions
        test_functions = len(re.findall(r'def\s+(test_[a-zA-Z_][a-zA-Z0-9_]*)\s*\(', test_code))
        
        # Estimate: assume each test covers one function
        if target_functions > 0:
            result['coverage'] = min(1.0, test_functions / target_functions)
            result['details'] = {
                'target_functions': target_functions,
                'test_functions': test_functions
            }
    except Exception:
        result['coverage'] = 0.5  # Default estimate
    
    return result


def calculate_weighted_score(result):
    """
    Calculate weighted total score.
    
    Weights:
    - Test Pass Rate: 40%
    - Speed Score: 20%
    - Code Quality: 15%
    - Safety: 15%
    - Improvement: 10%
    """
    return (
        result.test_pass_rate * 0.40 +
        result.speed_score * 0.20 +
        result.code_quality_score * 0.15 +
        result.safety_score * 0.15 +
        result.improvement_score * 0.10
    )


def calculate_speed_score(execution_time, max_time):
    """Calculate speed score with diminishing returns."""
    if execution_time >= max_time:
        return 0.0
    
    # Exponential decay - very fast = 1.0, half max = 0.5
    ratio = execution_time / max_time
    return max(0.0, 1.0 - (ratio ** 0.5))


def calculate_simplicity(workspace_path):
    """
    Calculate code simplicity score.
    
    Factors:
    - Line count (penalty if too long)
    - Nesting depth
    - Function length
    - Comment density
    """
    target_path = os.path.join(workspace_path, 'target.py')
    
    if not os.path.exists(target_path):
        return 0.5
    
    try:
        with open(target_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Count non-empty, non-comment lines
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        line_count = len(code_lines)
        
        # Penalty for excessive lines (soft cap at 100)
        line_penalty = 0.0
        if line_count > 100:
            line_penalty = min(0.3, (line_count - 100) / 200)
        
        # Calculate max nesting depth
        max_indent = 0
        for line in lines:
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                indent_level = indent // 4
                max_indent = max(max_indent, indent_level)
        
        # Penalty for deep nesting (soft cap at 3)
        nesting_penalty = 0.0
        if max_indent > 3:
            nesting_penalty = min(0.2, (max_indent - 3) * 0.05)
        
        # Bonus for good comment density (10-20% is ideal)
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        comment_ratio = comment_lines / max(1, len(lines))
        comment_bonus = 0.0
        if 0.1 <= comment_ratio <= 0.25:
            comment_bonus = 0.1
        
        # Calculate score
        simplicity = 1.0 - line_penalty - nesting_penalty + comment_bonus
        
        return max(0.0, min(1.0, simplicity))
        
    except Exception:
        return 0.5


def calculate_code_quality(workspace_path):
    """
    Calculate code quality score using AST analysis.
    
    Factors:
    - Function count vs file size
    - Docstring presence
    - Naming conventions
    - Cyclomatic complexity (basic)
    """
    target_path = os.path.join(workspace_path, 'target.py')
    
    if not os.path.exists(target_path):
        return 0.5
    
    try:
        with open(target_path, 'r') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        score = 1.0
        
        # Count functions and classes
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Docstring check (bonus for documented code)
        docstring_count = 0
        for func in functions:
            if ast.get_docstring(func):
                docstring_count += 1
        
        if functions:
            docstring_ratio = docstring_count / len(functions)
            score += docstring_ratio * 0.2
        
        # Naming convention check (snake_case for functions)
        naming_issues = 0
        for func in functions:
            if not re.match(r'^[a-z_][a-z0-9_]*$', func.name):
                naming_issues += 1
        
        if functions:
            naming_penalty = (naming_issues / len(functions)) * 0.1
            score -= naming_penalty
        
        # Cyclomatic complexity (basic - count branches)
        total_complexity = 0
        for func in functions:
            complexity = 1
            for node in ast.walk(func):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            total_complexity += complexity
        
        # Penalty for high complexity (>10 per function average)
        if functions:
            avg_complexity = total_complexity / len(functions)
            if avg_complexity > 10:
                score -= min(0.2, (avg_complexity - 10) * 0.02)
        
        return max(0.0, min(1.0, score))
        
    except Exception:
        return 0.5


def calculate_safety_score(test_pass_rate, execution_time, timeout):
    """
    Calculate safety score.
    
    Factors:
    - Test pass rate (critical)
    - No timeout
    - No errors
    """
    score = 1.0
    
    # Heavy penalty for test failures
    if test_pass_rate < 1.0:
        score -= (1.0 - test_pass_rate) * 2.0
    
    # Penalty for near-timeout
    if execution_time > timeout * 0.8:
        score -= 0.2
    
    return max(0.0, min(1.0, score))


def calculate_improvement_score(previous_score, current_score, claimed_improvement):
    """
    Calculate improvement score.
    
    Verifies if the change actually improved anything.
    Detects hallucination (claiming improvement that doesn't exist).
    """
    if previous_score is None:
        return 0.5  # No baseline, neutral
    
    delta = current_score - previous_score
    
    # Score based on improvement magnitude
    if delta > 0.01:
        improvement_score = min(1.0, 0.5 + delta * 10)
    elif delta > 0:
        improvement_score = 0.5 + delta
    else:
        improvement_score = max(0.0, 0.5 + delta)
    
    return improvement_score


def validate_syntax(file_path):
    """Validate Python syntax of a file."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        
        compile(source, file_path, 'exec')
        return True, None
        
    except SyntaxError as e:
        return False, f"Syntax error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, str(e)


def count_lines_changed(diff_text):
    """Count lines changed in a diff."""
    if not diff_text:
        return 0
    
    changed = 0
    for line in diff_text.split('\n'):
        if line.startswith('+') or line.startswith('-'):
            if not line.startswith('+++') and not line.startswith('---'):
                changed += 1
    
    return changed


def get_file_size(file_path):
    """Get file size in bytes."""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0


def detect_hallucination(claimed_improvement, actual_metrics):
    """
    Detect if LLM is hallucinating improvements.
    
    Returns:
        tuple: (is_hallucinating, confidence, explanation)
    """
    if not claimed_improvement:
        return False, 0.0, "No claim to verify"
    
    hallucinations = []
    
    # Check for common hallucination patterns
    claim_lower = claimed_improvement.lower()
    
    # Pattern 1: Claims speed improvement but execution time didn't improve
    if any(word in claim_lower for word in ['faster', 'speed', 'optimize', 'performance']):
        if actual_metrics.get('execution_time', 0) >= actual_metrics.get('previous_time', 0):
            hallucinations.append("Claimed speed improvement not verified")
    
    # Pattern 2: Claims test fixes but tests still fail
    if any(word in claim_lower for word in ['fix', 'test', 'bug', 'error']):
        if actual_metrics.get('test_pass_rate', 1.0) < 1.0:
            hallucinations.append("Claimed fix but tests still failing")
    
    # Pattern 3: Claims simplification but code grew
    if any(word in claim_lower for word in ['simplif', 'reduce', 'clean', 'refactor']):
        if actual_metrics.get('lines_after', 0) > actual_metrics.get('lines_before', 0) * 1.1:
            hallucinations.append("Claimed simplification but code grew")
    
    if hallucinations:
        return True, 0.8, "; ".join(hallucinations)
    
    return False, 0.0, "Claim appears valid"


if __name__ == "__main__":
    # Run evaluation and print detailed results
    result = evaluate()
    
    print("=== Advanced Evaluation Results ===")
    print(f"Status: {result.status}")
    print(f"Test Pass Rate: {result.test_pass_rate:.2%}")
    print(f"Execution Time: {result.execution_time:.4f}s")
    print(f"Speed Score: {result.speed_score:.2f}")
    print(f"Simplicity Score: {result.simplicity_score:.2f}")
    print(f"Code Quality Score: {result.code_quality_score:.2f}")
    print(f"Safety Score: {result.safety_score:.2f}")
    print(f"Improvement Score: {result.improvement_score:.2f}")
    print(f"Total Score: {result.total_score:.4f}")
    
    if result.hallucination_penalty > 0:
        print(f"⚠️ Hallucination Penalty: -{result.hallucination_penalty:.2f}")
    
    if result.error:
        print(f"Error: {result.error}")

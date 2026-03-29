"""
Evaluation Engine

Implements scoring logic as defined in core/evaluation.md

Score = (Test Pass Rate × 0.70) + (Speed Score × 0.20) + (Simplicity Score × 0.10)
"""

import time
import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'workspace'))


class EvaluationResult:
    """Holds evaluation results."""
    
    def __init__(self):
        self.test_pass_rate = 0.0
        self.execution_time = 0.0
        self.speed_score = 0.0
        self.simplicity_score = 0.0
        self.total_score = 0.0
        self.status = "pending"  # pending, accepted, rejected
        self.error = None
        self.details = {}
    
    def to_dict(self):
        return {
            "test_pass_rate": self.test_pass_rate,
            "execution_time": self.execution_time,
            "speed_score": self.speed_score,
            "simplicity_score": self.simplicity_score,
            "total_score": self.total_score,
            "status": self.status,
            "error": self.error,
            "details": self.details
        }


def evaluate(workspace_path=None, timeout=5.0):
    """
    Evaluate the current workspace code.
    
    Args:
        workspace_path: Path to workspace directory
        timeout: Maximum execution time in seconds
        
    Returns:
        EvaluationResult object
    """
    result = EvaluationResult()
    
    if workspace_path is None:
        workspace_path = os.path.join(os.path.dirname(__file__), '..', 'workspace')
    
    try:
        # Run tests with timeout
        start_time = time.time()
        
        from tests import run_tests
        test_pass_rate = run_tests()
        
        elapsed = time.time() - start_time
        result.execution_time = elapsed
        
        # Check timeout
        if elapsed > timeout:
            result.status = "rejected"
            result.error = "timeout"
            result.execution_time = elapsed
            return result
        
        result.test_pass_rate = test_pass_rate
        
        # Calculate speed score
        result.speed_score = max(0.0, 1.0 - (elapsed / timeout))
        
        # Calculate simplicity score
        result.simplicity_score = calculate_simplicity(workspace_path)
        
        # Calculate total score
        result.total_score = calculate_total_score(
            result.test_pass_rate,
            result.speed_score,
            result.simplicity_score
        )
        
        result.status = "accepted" if result.total_score > 0 else "rejected"
        
    except TimeoutError:
        result.status = "rejected"
        result.error = "timeout"
        result.execution_time = timeout
    except Exception as e:
        result.status = "rejected"
        result.error = str(e)
        result.details["exception_type"] = type(e).__name__
    
    return result


def calculate_total_score(test_pass_rate, speed_score, simplicity_score):
    """
    Calculate weighted total score.
    
    Score = (Test Pass Rate × 0.70) + (Speed Score × 0.20) + (Simplicity Score × 0.10)
    """
    return (
        test_pass_rate * 0.70 +
        speed_score * 0.20 +
        simplicity_score * 0.10
    )


def calculate_simplicity(workspace_path):
    """
    Calculate code simplicity score.
    
    Factors:
    - Line count (penalty if too long)
    - Nesting depth
    - Function length
    
    Returns:
        float: Simplicity score from 0.0 to 1.0
    """
    target_path = os.path.join(workspace_path, 'target.py')
    
    if not os.path.exists(target_path):
        return 0.5  # Default if file missing
    
    try:
        with open(target_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        line_count = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        # Penalty for excessive lines
        line_penalty = 0.0
        if line_count > 100:
            line_penalty = min(0.5, (line_count - 100) / 100)
        
        # Calculate max nesting depth
        max_indent = 0
        for line in lines:
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                indent_level = indent // 4
                max_indent = max(max_indent, indent_level)
        
        # Penalty for deep nesting
        nesting_penalty = 0.0
        if max_indent > 3:
            nesting_penalty = min(0.3, (max_indent - 3) * 0.1)
        
        # Base simplicity score with penalties
        simplicity = 1.0 - line_penalty - nesting_penalty
        
        return max(0.0, min(1.0, simplicity))
        
    except Exception:
        return 0.5


def validate_syntax(file_path):
    """
    Validate Python syntax of a file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        tuple: (is_valid, error_message)
    """
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
    """
    Count lines changed in a diff.
    
    Args:
        diff_text: Unified diff string
        
    Returns:
        int: Number of lines changed
    """
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


if __name__ == "__main__":
    # Run evaluation and print results
    result = evaluate()
    
    print("=== Evaluation Results ===")
    print(f"Status: {result.status}")
    print(f"Test Pass Rate: {result.test_pass_rate:.2%}")
    print(f"Execution Time: {result.execution_time:.4f}s")
    print(f"Speed Score: {result.speed_score:.2f}")
    print(f"Simplicity Score: {result.simplicity_score:.2f}")
    print(f"Total Score: {result.total_score:.4f}")
    
    if result.error:
        print(f"Error: {result.error}")

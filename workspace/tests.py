"""
Test Suite for target.py (Fibonacci)

Defines correctness criteria.
Do NOT remove tests - only add or refine.
"""

from target import fibonacci, fibonacci_sequence


def run_tests():
    """
    Run all tests and return pass rate.
    
    Returns:
        float: Pass rate from 0.0 to 1.0
    """
    test_cases = get_test_cases()
    
    if not test_cases:
        return 0.0
    
    passed = 0
    total = len(test_cases)
    
    for test_func, test_name in test_cases:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"Test '{test_name}' failed with error: {e}")
    
    return passed / total


def get_test_cases():
    """Get list of test functions."""
    return [
        (test_fibonacci_0, "test_fibonacci_0"),
        (test_fibonacci_1, "test_fibonacci_1"),
        (test_fibonacci_5, "test_fibonacci_5"),
        (test_fibonacci_10, "test_fibonacci_10"),
        (test_fibonacci_sequence, "test_fibonacci_sequence"),
        (test_fibonacci_empty_sequence, "test_fibonacci_empty_sequence"),
    ]


def test_fibonacci_0():
    """Test fibonacci(0)."""
    return fibonacci(0) == 0


def test_fibonacci_1():
    """Test fibonacci(1)."""
    return fibonacci(1) == 1


def test_fibonacci_5():
    """Test fibonacci(5)."""
    return fibonacci(5) == 5


def test_fibonacci_10():
    """Test fibonacci(10)."""
    return fibonacci(10) == 55


def test_fibonacci_sequence():
    """Test fibonacci_sequence."""
    return fibonacci_sequence(7) == [0, 1, 1, 2, 3, 5, 8]


def test_fibonacci_empty_sequence():
    """Test fibonacci_sequence with 0."""
    return fibonacci_sequence(0) == []


if __name__ == "__main__":
    pass_rate = run_tests()
    print(f"Test Pass Rate: {pass_rate * 100:.1f}%")

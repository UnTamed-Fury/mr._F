"""
Goal:
- Calculate fibonacci numbers efficiently

Constraints:
- Must pass tests in tests.py
- Must not modify function signatures
- Must use only standard library
"""

from typing import List


def fibonacci(n: int) -> int:
    """
    Calculate the nth fibonacci number.

    Args:
        n: The position in fibonacci sequence (0-indexed)

    Returns:
        The nth fibonacci number
    """
    # Optimized iterative implementation
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_sequence(count: int) -> List[int]:
    """
    Generate first n fibonacci numbers.

    Args:
        count: How many numbers to generate

    Returns:
        List of first n fibonacci numbers
    """
    # Optimized to avoid redundant calculations
    if count <= 0:
        return []
    result = [0, 1]
    for i in range(2, count):
        result.append(result[-1] + result[-2])
    return result[:count]
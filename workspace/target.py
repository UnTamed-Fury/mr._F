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
        n: The position in fibonacci sequence (0-indexed). 
           For n <= 0, returns 0.

    Returns:
        The nth fibonacci number. For n=0 returns 0, n=1 returns 1.

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(5)
        5

    Time complexity: O(n)
    Space complexity: O(1)
    """
    # Optimized iterative implementation
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a: int = 0
    b: int = 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_sequence(count: int) -> List[int]:
    """
    Generate first n fibonacci numbers.

    Args:
        count: How many numbers to generate. If count <= 0, returns an empty list.

    Returns:
        List of first count fibonacci numbers, starting with 0.
        For count=1 returns [0]; for count=2 returns [0, 1].

    Examples:
        >>> fibonacci_sequence(0)
        []
        >>> fibonacci_sequence(1)
        [0]
        >>> fibonacci_sequence(5)
        [0, 1, 1, 2, 3]

    Time complexity: O(n)
    Space complexity: O(n)
    """
    # Optimized to avoid redundant calculations
    if count <= 0:
        return []
    result: List[int] = [0, 1]
    for i in range(2, count):
        result.append(result[-1] + result[-2])
    return result[:count]
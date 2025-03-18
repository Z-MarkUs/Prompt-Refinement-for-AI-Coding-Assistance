class Solution:
    def minOperations(self, n: int) -> int:
        return ((n + 1) // 4) * ((n - 1) // 2)
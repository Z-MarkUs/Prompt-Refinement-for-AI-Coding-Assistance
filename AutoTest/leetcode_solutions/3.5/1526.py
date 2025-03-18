from typing import List

class Solution:
    def minNumberOperations(self, target: List[int]) -> int:
        n = len(target)
        if n == 0:
            return 0
        
        result = target[0]
        for i in range(1, n):
            result += max(0, target[i] - target[i-1])
        
        return result
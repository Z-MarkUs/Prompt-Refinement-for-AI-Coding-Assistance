from typing import List

class Solution:
    def maxDistance(self, position: List[int], m: int) -> int:
        position.sort()
        left, right = 0, position[-1] - position[0]
        while left < right:
            mid = (left + right + 1) // 2
            if self.check(position, m, mid):
                left = mid
            else:
                right = mid - 1
        return left
    
    def check(self, position, m, mid):
        count = 1
        prev = position[0]
        for i in range(1, len(position)):
            if position[i] - prev >= mid:
                count += 1
                prev = position[i]
        return count >= m
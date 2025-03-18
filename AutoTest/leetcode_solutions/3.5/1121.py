from typing import List

class Solution:
    def canDivideIntoSubsequences(self, nums: List[int], k: int) -> bool:
        count = 1
        max_count = 1
        
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1]:
                count += 1
                max_count = max(max_count, count)
            else:
                count = 1
        
        return len(nums) >= k * max_count
class Solution:
    def maxNonOverlapping(self, nums: List[int], target: int) -> int:
        seen = {0}
        prefix_sum = 0
        count = 0
        
        for num in nums:
            prefix_sum += num
            if prefix_sum - target in seen:
                count += 1
                seen = {0}
                prefix_sum = 0
            else:
                seen.add(prefix_sum)
        
        return count
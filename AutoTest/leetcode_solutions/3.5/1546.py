class Solution:
    def maxNonOverlapping(self, nums: List[int], target: int) -> int:
        dp = {0}
        prefix_sum = 0
        count = 0
        
        for num in nums:
            prefix_sum += num
            if prefix_sum - target in dp:
                count += 1
                dp = {0}
                prefix_sum = 0
            dp.add(prefix_sum)
        
        return count
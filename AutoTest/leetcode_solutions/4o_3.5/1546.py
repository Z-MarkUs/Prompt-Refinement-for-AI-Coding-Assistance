class Solution:
    def maxNonOverlapping(self, nums: List[int], target: int) -> int:
        prefix_sum = {0: -1}
        current_sum = 0
        last_end = -1
        count = 0
        
        for i in range(len(nums)):
            current_sum += nums[i]
            if current_sum - target in prefix_sum and prefix_sum[current_sum - target] > last_end:
                count += 1
                last_end = i
            prefix_sum[current_sum] = i
        
        return count
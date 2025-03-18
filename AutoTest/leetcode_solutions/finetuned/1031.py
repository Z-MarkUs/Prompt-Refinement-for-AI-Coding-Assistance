class Solution:
    def maxSumTwoNoOverlap(self, nums: List[int], firstLen: int, secondLen: int) -> int:
        prefix_sum = [0] * (len(nums) + 1)
        for i in range(len(nums)):
            prefix_sum[i + 1] = prefix_sum[i] + nums[i]
        
        max_sum = 0
        max_first = 0
        max_second = 0
        
        for i in range(firstLen, len(nums) + 1):
            max_first = max(max_first, prefix_sum[i] - prefix_sum[i - firstLen])
            max_sum = max(max_sum, max_first + prefix_sum[i] - prefix_sum[i - firstLen])
        
        for i in range(secondLen, len(nums) + 1):
            max_second = max(max_second, prefix_sum[i] - prefix_sum[i - secondLen])
            max_sum = max(max(max_sum, max_second + prefix_sum[i] - prefix_sum[i - secondLen]), max_first)
        
        return max_sum
class Solution:
    def maxSumTwoNoOverlap(self, nums: List[int], firstLen: int, secondLen: int) -> int:
        n = len(nums)
        prefix_sum = [0] * (n + 1)
        for i in range(n):
            prefix_sum[i + 1] = prefix_sum[i] + nums[i]
        
        max_sum = 0
        max_first = 0
        max_second = 0
        
        for i in range(firstLen, n):
            max_first = max(max_first, prefix_sum[i] - prefix_sum[i - firstLen])
            max_second = max(max_second, prefix_sum[i] - prefix_sum[i - secondLen])
            max_sum = max(max_sum, max_first + prefix_sum[i + 1] - prefix_sum[i - firstLen + 1], max_second + prefix_sum[i + 1] - prefix_sum[i - secondLen + 1])
        
        return max_sum
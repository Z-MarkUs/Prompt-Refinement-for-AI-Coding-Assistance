class Solution:
    def rangeSum(self, nums: List[int], n: int, left: int, right: int) -> int:
        MOD = 10**9 + 7
        prefix_sum = [0]
        for num in nums:
            prefix_sum.append(prefix_sum[-1] + num)
        
        subarray_sums = []
        for i in range(1, n+1):
            for j in range(i, n+1):
                subarray_sums.append(prefix_sum[j] - prefix_sum[i-1])
        
        subarray_sums.sort()
        
        result = sum(subarray_sums[left-1:right]) % MOD
        return result
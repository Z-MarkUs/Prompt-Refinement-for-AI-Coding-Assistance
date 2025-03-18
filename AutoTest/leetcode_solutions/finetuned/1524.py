class Solution:
    def numOfSubarrays(self, arr: List[int]) -> int:
        MOD = 10**9 + 7
        odd_count = 0
        even_count = 1
        subarray_count = 0
        
        prefix_sum = 0
        for num in arr:
            prefix_sum += num
            if prefix_sum % 2 == 0:
                subarray_count = (subarray_count + odd_count) % MOD
                even_count += 1
            else:
                subarray_count = (subarray_count + even_count) % MOD
                odd_count += 1
        
        return subarray_count % MOD
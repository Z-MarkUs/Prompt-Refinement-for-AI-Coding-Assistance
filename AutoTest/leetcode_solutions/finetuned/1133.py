class Solution:
    def largestUniqueNumber(self, nums: List[int]) -> int:
        num_freq = {}
        for num in nums:
            if num in num_freq:
                num_freq[num] += 1
            else:
                num_freq[num] = 1
        
        unique_nums = [key for key, value in num_freq.items() if value == 1]
        
        if not unique_nums:
            return -1
        
        return max(unique_nums)
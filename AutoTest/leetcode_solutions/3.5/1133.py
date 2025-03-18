class Solution:
    def largestUniqueNumber(self, nums: List[int]) -> int:
        num_count = {}
        for num in nums:
            if num in num_count:
                num_count[num] += 1
            else:
                num_count[num] = 1
        
        unique_nums = [key for key, value in num_count.items() if value == 1]
        
        if not unique_nums:
            return -1
        else:
            return max(unique_nums)
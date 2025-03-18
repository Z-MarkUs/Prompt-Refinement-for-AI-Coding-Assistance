class Solution:
    def getMaxLen(self, nums: List[int]) -> int:
        max_len = 0
        neg_count = 0
        start_index = 0
        
        for i in range(len(nums)):
            if nums[i] == 0:
                neg_count = 0
                start_index = i + 1
            elif nums[i] < 0:
                neg_count += 1
            
            if neg_count % 2 == 0:
                max_len = max(max_len, i - start_index + 1)
        
        neg_count = 0
        start_index = len(nums)
        
        for i in range(len(nums) - 1, -1, -1):
            if nums[i] == 0:
                neg_count = 0
                start_index = i
            elif nums[i] < 0:
                neg_count += 1
            
            if neg_count % 2 == 0:
                max_len = max(max_len, start_index - i)
        
        return max_len
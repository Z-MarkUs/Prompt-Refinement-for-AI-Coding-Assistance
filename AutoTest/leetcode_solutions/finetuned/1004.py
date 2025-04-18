class Solution:
    def longestOnes(self, nums: List[int], k: int) -> int:
        left = 0
        right = 0
        max_ones = 0
        zero_count = 0
        
        while right < len(nums):
            if nums[right] == 0:
                zero_count += 1
            
            while zero_count > k:
                if nums[left] == 0:
                    zero_count -= 1
                left += 1
            
            max_ones = max(max_ones, right - left + 1)
            right += 1
        
        return max_ones
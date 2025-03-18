class Solution:
    def missingElement(self, nums: List[int], k: int) -> int:
        left, right = 0, len(nums) - 1
        
        while left < right:
            mid = left + (right - left) // 2
            missing_count = nums[mid] - nums[0] - mid
            
            if missing_count < k:
                left = mid + 1
            else:
                right = mid
        
        return nums[0] + k + left - 1
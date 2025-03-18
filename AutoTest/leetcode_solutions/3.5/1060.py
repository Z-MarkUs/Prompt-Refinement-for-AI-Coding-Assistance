class Solution:
    def missingElement(self, nums: List[int], k: int) -> int:
        left, right = 0, len(nums) - 1
        
        while left < right:
            mid = left + (right - left) // 2
            missing_count = nums[mid] - nums[left] - (mid - left)
            
            if missing_count >= k:
                right = mid
            else:
                k -= missing_count
                left = mid + 1
        
        return nums[left] + k
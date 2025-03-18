class Solution:
    def isMajorityElement(self, nums: List[int], target: int) -> bool:
        def findFirstOccurrence(nums, target):
            left, right = 0, len(nums) - 1
            while left < right:
                mid = left + (right - left) // 2
                if nums[mid] < target:
                    left = mid + 1
                else:
                    right = mid
            return left if nums[left] == target else -1
        
        def findLastOccurrence(nums, target):
            left, right = 0, len(nums) - 1
            while left < right:
                mid = left + (right - left + 1) // 2
                if nums[mid] > target:
                    right = mid - 1
                else:
                    left = mid
            return left if nums[left] == target else -1
        
        first = findFirstOccurrence(nums, target)
        last = findLastOccurrence(nums, target)
        
        if first != -1 and last != -1:
            count = last - first + 1
            return count > len(nums) / 2
        else:
            return False
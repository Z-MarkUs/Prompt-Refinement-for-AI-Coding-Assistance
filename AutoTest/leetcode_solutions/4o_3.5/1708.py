class Solution:
    def largestSubarray(self, nums: List[int], k: int) -> List[int]:
        start = 0
        for i in range(1, len(nums) - k + 1):
            if nums[i:i+k] > nums[start:start+k]:
                start = i
        return nums[start:start+k]
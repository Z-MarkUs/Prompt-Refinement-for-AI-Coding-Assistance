from typing import List

class Solution:
    def largestSubarray(self, nums: List[int], k: int) -> List[int]:
        start = 0
        max_index = 0
        for i in range(1, len(nums) - k + 1):
            if nums[i] > nums[max_index]:
                max_index = i
            if i - start == k:
                start += 1
                max_index = start
        return nums[max_index:max_index + k]
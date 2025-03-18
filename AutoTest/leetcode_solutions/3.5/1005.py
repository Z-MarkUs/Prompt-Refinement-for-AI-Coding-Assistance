class Solution:
    def largestSumAfterKNegations(self, nums: List[int], k: int) -> int:
        nums.sort()
        i = 0
        while k > 0 and i < len(nums) and nums[i] < 0:
            nums[i] = -nums[i]
            k -= 1
            i += 1
        if k % 2 == 1:
            if i == 0:
                nums.sort()
                nums[0] = -nums[0]
            else:
                if i == len(nums):
                    nums[-1] = -nums[-1]
                else:
                    if nums[i] < nums[i-1]:
                        nums[i] = -nums[i]
                    else:
                        nums[i-1] = -nums[i-1]
        return sum(nums)
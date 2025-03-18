class Solution:
    def largestSumAfterKNegations(self, nums: List[int], k: int) -> int:
        nums.sort(key=abs, reverse=True)
        i = 0
        while k > 0 and i < len(nums):
            if nums[i] < 0:
                nums[i] = -nums[i]
                k -= 1
            elif nums[i] == 0:
                break
            else:
                if k % 2 == 1:
                    if i == 0 or abs(nums[i]) < abs(nums[i - 1]):
                        nums[i] = -nums[i]
                    break
            i += 1
        return sum(nums)
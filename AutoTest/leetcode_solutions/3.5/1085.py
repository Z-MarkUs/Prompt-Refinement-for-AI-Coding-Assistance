from typing import List

class Solution:
    def sumOfDigits(self, nums: List[int]) -> int:
        min_num = min(nums)
        sum_digits = sum(int(digit) for digit in str(min_num))
        return 1 if sum_digits % 2 == 0 else 0
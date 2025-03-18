class Solution:
    def sumOfDigits(self, nums: List[int]) -> int:
        min_val = min(nums)
        digit_sum = sum(int(digit) for digit in str(min_val))
        return 1 if digit_sum % 2 == 0 else 0
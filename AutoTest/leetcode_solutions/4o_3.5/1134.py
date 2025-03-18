class Solution:
    def isArmstrong(self, n: int) -> bool:
        num_str = str(n)
        k = len(num_str)
        armstrong_sum = sum(int(digit) ** k for digit in num_str)
        return armstrong_sum == n

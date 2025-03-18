class Solution:
    def isArmstrong(self, n: int) -> bool:
        k = len(str(n))
        total = 0
        temp = n
        while temp > 0:
            digit = temp % 10
            total += digit ** k
            temp //= 10
        return total == n
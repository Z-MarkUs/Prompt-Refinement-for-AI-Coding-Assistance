class Solution:
    def isArmstrong(self, n: int) -> bool:
        num_str = str(n)
        k = len(num_str)
        total = 0
        
        for digit in num_str:
            total += int(digit) ** k
        
        return total == n
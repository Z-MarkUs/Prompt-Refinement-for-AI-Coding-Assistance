class Solution:
    def confusingNumber(self, n: int) -> bool:
        valid_rotations = {0: 0, 1: 1, 6: 9, 8: 8, 9: 6}
        original = n
        rotated = 0
        
        while n > 0:
            digit = n % 10
            if digit not in valid_rotations:
                return False
            rotated = rotated * 10 + valid_rotations[digit]
            n //= 10
        
        return rotated != original
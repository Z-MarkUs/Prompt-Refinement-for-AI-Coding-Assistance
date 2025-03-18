class Solution:
    def confusingNumber(self, n: int) -> bool:
        rotations = {'0': '0', '1': '1', '6': '9', '8': '8', '9': '6'}
        num_str = str(n)
        rotated_num = ''
        
        for digit in num_str:
            if digit not in rotations:
                return False
            rotated_num = rotations[digit] + rotated_num
        
        return rotated_num != num_str
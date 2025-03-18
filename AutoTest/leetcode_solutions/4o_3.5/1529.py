class Solution:
    def minFlips(self, target: str) -> int:
        operations = 0
        prev_bit = '0'
        
        for bit in target:
            if bit != prev_bit:
                operations += 1
                prev_bit = bit
        
        return operations

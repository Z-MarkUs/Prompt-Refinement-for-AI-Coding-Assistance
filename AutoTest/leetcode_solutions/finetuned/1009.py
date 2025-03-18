class Solution:
    def bitwiseComplement(self, n: int) -> int:
        binary_n = bin(n)[2:]
        complement = ''.join(['1' if bit == '0' else '0' for bit in binary_n])
        return int(complement, 2)
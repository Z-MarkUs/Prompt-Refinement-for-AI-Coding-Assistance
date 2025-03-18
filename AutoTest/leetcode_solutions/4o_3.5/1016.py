class Solution:
    def queryString(self, s: str, n: int) -> bool:
        for k in range(1, n+1):
            binary_k = bin(k)[2:]
            if binary_k not in s:
                return False
        return True
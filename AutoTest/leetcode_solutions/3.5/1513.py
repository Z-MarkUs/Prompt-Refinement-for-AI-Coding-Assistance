class Solution:
    def numSub(self, s: str) -> int:
        count = 0
        result = 0
        mod = 10**9 + 7
        
        for char in s:
            if char == '1':
                count += 1
                result = (result + count) % mod
            else:
                count = 0
        
        return result
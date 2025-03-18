class Solution:
    def canConvertString(self, s: str, t: str, k: int) -> bool:
        if len(s) != len(t):
            return False
        
        shifts = [0] * 26
        
        for i in range(len(s)):
            diff = (ord(t[i]) - ord(s[i]) + 26) % 26
            if diff != 0 and shifts[diff] * 26 + diff > k:
                return False
            shifts[diff] += 1
        
        return True
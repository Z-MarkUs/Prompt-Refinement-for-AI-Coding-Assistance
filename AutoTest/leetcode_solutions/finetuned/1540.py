class Solution:
    def canConvertString(self, s: str, t: str, k: int) -> bool:
        if len(s) != len(t):
            return False
        
        shifts = [0] * 26
        
        for i in range(len(s)):
            diff = (ord(t[i]) - ord(s[i]) + 26) % 26
            if diff != 0 and shifts[diff] == 0:
                shifts[diff] = diff
            elif diff != 0:
                shifts[diff] += 26
        
        for shift in shifts:
            if shift > k or (shift == 0 and k < 26):
                return False
        
        return True
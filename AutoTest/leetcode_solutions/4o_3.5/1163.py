class Solution:
    def lastSubstring(self, s: str) -> str:
        n = len(s)
        i, j, k = 0, 1, 0
        
        while j + k < n:
            if s[i+k] == s[j+k]:
                k += 1
            elif s[i+k] < s[j+k]:
                i = j
                j += 1
                k = 0
            else:
                j += k + 1
                k = 0
        
        return s[i:]
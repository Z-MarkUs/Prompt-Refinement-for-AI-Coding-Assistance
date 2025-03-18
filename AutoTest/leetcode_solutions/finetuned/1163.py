class Solution:
    def lastSubstring(self, s: str) -> str:
        n = len(s)
        i = n - 1
        j = n - 2
        
        while j >= 0:
            if s[i] == s[j]:
                i -= 1
                j -= 1
            elif s[i] < s[j]:
                j -= 1
            else:
                i = i - 1 + j
                j = i - 1
        
        return s[i:]
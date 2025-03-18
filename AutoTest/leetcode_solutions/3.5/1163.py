class Solution:
    def lastSubstring(self, s: str) -> str:
        n = len(s)
        i, j, k = 0, 1, 0
        while j + k < n:
            if s[i+k] == s[j+k]:
                k += 1
                continue
            elif s[i+k] < s[j+k]:
                i = max(i+k+1, j)
            else:
                j = max(j+k+1, i)
            k = 0
        return s[i:]
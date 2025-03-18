class Solution:
    def countLetters(self, s: str) -> int:
        count = 0
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            n = j - i
            count += n * (n + 1) // 2
            i = j
        return count
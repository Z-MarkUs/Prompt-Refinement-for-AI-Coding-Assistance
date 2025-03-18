class Solution:
    def longestDecomposition(self, text: str) -> int:
        n = len(text)
        for i in range(n // 2):
            if text[:i + 1] == text[n - 1 - i:]:
                return 2 + self.longestDecomposition(text[i + 1:n - 1 - i])
        return 1 if n > 0 else 0
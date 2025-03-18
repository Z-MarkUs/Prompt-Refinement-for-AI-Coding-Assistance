class Solution:
    def maxRepeating(self, sequence: str, word: str) -> int:
        max_repeating = 0
        for i in range(len(sequence) // len(word)):
            if word * (i + 1) in sequence:
                max_repeating = i + 1
        return max_repeating
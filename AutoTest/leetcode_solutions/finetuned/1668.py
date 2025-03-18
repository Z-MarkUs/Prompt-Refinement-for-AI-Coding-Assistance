class Solution:
    def maxRepeating(self, sequence: str, word: str) -> int:
        if word not in sequence:
            return 0
        
        max_repeats = 1
        while word * max_repeats in sequence:
            max_repeats += 1
        
        return max_repeats - 1
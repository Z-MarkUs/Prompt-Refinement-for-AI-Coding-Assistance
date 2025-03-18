class Solution:
    def commonChars(self, words: List[str]) -> List[str]:
        result = []
        min_freq = [float('inf')] * 26
        
        for word in words:
            freq = [0] * 26
            for char in word:
                freq[ord(char) - ord('a')] += 1
            for i in range(26):
                min_freq[i] = min(min_freq[i], freq[i])
        
        for i in range(26):
            result.extend([chr(i + ord('a'))] * min_freq[i])
        
        return result
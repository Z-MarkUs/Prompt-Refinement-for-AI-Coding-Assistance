class Solution:
    def countCharacters(self, words: List[str], chars: str) -> int:
        def count_frequency(s):
            freq = [0] * 26
            for char in s:
                freq[ord(char) - ord('a')] += 1
            return freq
        
        total_length = 0
        chars_freq = count_frequency(chars)
        
        for word in words:
            word_freq = count_frequency(word)
            constructible = True
            
            for i in range(26):
                if word_freq[i] > chars_freq[i]:
                    constructible = False
                    break
            
            if constructible:
                total_length += len(word)
        
        return total_length
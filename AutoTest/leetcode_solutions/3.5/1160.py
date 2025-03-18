class Solution:
    def countCharacters(self, words: List[str], chars: str) -> int:
        total_length = 0
        char_count = Counter(chars)
        
        for word in words:
            word_count = Counter(word)
            valid = True
            
            for char, count in word_count.items():
                if char not in char_count or count > char_count[char]:
                    valid = False
                    break
            
            if valid:
                total_length += len(word)
        
        return total_length
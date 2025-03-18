from typing import List

class Solution:
    def longestStrChain(self, words: List[str]) -> int:
        words.sort(key=len)
        word_dict = {}
        max_length = 1
        
        for word in words:
            word_dict[word] = 1
            for i in range(len(word)):
                predecessor = word[:i] + word[i+1:]
                if predecessor in word_dict:
                    word_dict[word] = max(word_dict[word], word_dict[predecessor] + 1)
            max_length = max(max_length, word_dict[word])
        
        return max_length
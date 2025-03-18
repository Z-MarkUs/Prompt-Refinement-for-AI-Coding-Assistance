class Solution:
    def arrayStringsAreEqual(self, word1: List[str], word2: List[str]) -> bool:
        concat_word1 = ''.join(word1)
        concat_word2 = ''.join(word2)
        
        return concat_word1 == concat_word2
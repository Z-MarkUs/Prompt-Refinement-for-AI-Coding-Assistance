class Solution:
    def longestStrChain(self, words: List[str]) -> int:
        def is_predecessor(word1, word2):
            if len(word2) != len(word1) + 1:
                return False
            i, j = 0, 0
            while i < len(word1) and j < len(word2):
                if word1[i] != word2[j]:
                    j += 1
                else:
                    i += 1
                    j += 1
            return i == len(word1)
        
        words.sort(key=len)
        dp = {}
        for word in words:
            dp[word] = 1
            for i in range(len(word)):
                predecessor = word[:i] + word[i+1:]
                if predecessor in dp:
                    dp[word] = max(dp[word], dp[predecessor] + 1)
        
        return max(dp.values())
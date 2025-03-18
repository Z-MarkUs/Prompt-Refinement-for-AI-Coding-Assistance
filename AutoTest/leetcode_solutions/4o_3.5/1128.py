class Solution:
    def numEquivDominoPairs(self, dominoes: List[List[int]) -> int:
        count = 0
        domino_freq = {}
        
        for domino in dominoes:
            domino.sort()
            domino_tuple = tuple(domino)
            if domino_tuple in domino_freq:
                count += domino_freq[domino_tuple]
                domino_freq[domino_tuple] += 1
            else:
                domino_freq[domino_tuple] = 1
        
        return count
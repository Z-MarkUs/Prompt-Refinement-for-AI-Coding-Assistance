class Solution:
    def numEquivDominoPairs(self, dominoes: List[List[int]) -> int:
        count = 0
        domino_dict = {}
        
        for domino in dominoes:
            domino.sort()
            domino_tuple = tuple(domino)
            if domino_tuple in domino_dict:
                count += domino_dict[domino_tuple]
                domino_dict[domino_tuple] += 1
            else:
                domino_dict[domino_tuple] = 1
        
        return count
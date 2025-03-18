from collections import defaultdict
from typing import List

class Solution:
    def numEquivDominoPairs(self, dominoes: List[List[int]]) -> int:
        count = defaultdict(int)
        res = 0
        for domino in dominoes:
            domino.sort()
            res += count[tuple(domino)]
            count[tuple(domino)] += 1
        return res
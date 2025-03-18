from typing import List

class Solution:
    def maxScoreSightseeingPair(self, values: List[int]) -> int:
        max_i_score = values[0]
        max_score = 0
        
        for j in range(1, len(values)):
            max_score = max(max_score, max_i_score + values[j] - j)
            max_i_score = max(max_i_score, values[j] + j)
        
        return max_score
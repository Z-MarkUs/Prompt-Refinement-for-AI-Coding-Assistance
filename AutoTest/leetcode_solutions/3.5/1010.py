class Solution:
    def numPairsDivisibleBy60(self, time: List[int]) -> int:
        count = 0
        remainder_count = [0] * 60
        
        for t in time:
            remainder = t % 60
            count += remainder_count[(60 - remainder) % 60]
            remainder_count[remainder] += 1
        
        return count
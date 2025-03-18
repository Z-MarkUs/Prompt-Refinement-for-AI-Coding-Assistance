class Solution:
    def numPairsDivisibleBy60(self, time: List[int]) -> int:
        remainder_count = [0] * 60
        pairs = 0
        
        for t in time:
            complement = (60 - t % 60) % 60
            pairs += remainder_count[complement]
            remainder_count[t % 60] += 1
        
        return pairs
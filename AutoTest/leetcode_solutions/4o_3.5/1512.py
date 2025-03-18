from typing import List

class Solution:
    def numIdenticalPairs(self, nums: List[int]) -> int:
        pairs = 0
        num_freq = {}
        
        for num in nums:
            if num in num_freq:
                pairs += num_freq[num]
                num_freq[num] += 1
            else:
                num_freq[num] = 1
        
        return pairs

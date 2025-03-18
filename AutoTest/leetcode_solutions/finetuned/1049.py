class Solution:
    def lastStoneWeightII(self, stones: List[int]) -> int:
        stones.sort()
        while len(stones) > 1:
            heaviest1 = stones.pop()
            heaviest2 = stones.pop()
            if heaviest1 != heaviest2:
                stones.append(abs(heaviest1 - heaviest2))
                stones.sort()
        return stones[0] if stones else 0
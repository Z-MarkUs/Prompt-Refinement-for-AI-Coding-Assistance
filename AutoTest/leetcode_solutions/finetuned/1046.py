class Solution:
    def lastStoneWeight(self, stones: List[int]) -> int:
        import heapq
        
        stones = [-stone for stone in stones]
        heapq.heapify(stones)
        
        while len(stones) > 1:
            heaviest1 = heapq.heappop(stones)
            heaviest2 = heapq.heappop(stones)
            
            if heaviest1 != heaviest2:
                heapq.heappush(stones, heaviest1 - heaviest2)
        
        return -stones[0] if stones else 0
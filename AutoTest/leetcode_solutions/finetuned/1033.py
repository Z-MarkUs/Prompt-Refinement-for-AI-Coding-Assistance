class Solution:
    def numMovesStones(self, a: int, b: int, c: int) -> List[int]:
        stones = [a, b, c]
        stones.sort()
        
        min_moves = 2 if stones[2] - stones[1] == 2 or stones[1] - stones[0] == 2 else 1
        max_moves = stones[2] - stones[1] - 1 + stones[1] - stones[0] - 1
        
        return [min_moves, max_moves]
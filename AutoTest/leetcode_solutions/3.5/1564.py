class Solution:
    def maxBoxesInWarehouse(self, boxes: List[int], warehouse: List[int]) -> int:
        piles.sort()
        n = len(piles) // 3
        return sum(piles[-2*n::3])
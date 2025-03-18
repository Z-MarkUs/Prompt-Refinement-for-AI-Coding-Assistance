from typing import List

class Solution:
    def allCellsDistOrder(self, rows: int, cols: int, rCenter: int, cCenter: int) -> List[List[int]]:
        result = []
        for r in range(rows):
            for c in range(cols):
                result.append([r, c])
        
        result.sort(key=lambda x: abs(x[0] - rCenter) + abs(x[1] - cCenter))
        
        return result
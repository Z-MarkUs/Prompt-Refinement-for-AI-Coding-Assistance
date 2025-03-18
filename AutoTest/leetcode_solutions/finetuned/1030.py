class Solution:
    def allCellsDistOrder(self, rows: int, cols: int, rCenter: int, cCenter: int) -> List[List[int]]:
        def distance(cell):
            return abs(cell[0] - rCenter) + abs(cell[1] - cCenter)
        
        cells = [[i, j] for i in range(rows) for j in range(cols)]
        return sorted(cells, key=distance)
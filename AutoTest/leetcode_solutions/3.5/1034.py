from typing import List

class Solution:
    def colorBorder(self, grid: List[List[int]], row: int, col: int, color: int) -> List[List[int]]:
        def dfs(i, j):
            if not (0 <= i < len(grid) and 0 <= j < len(grid[0]) and grid[i][j] == grid[row][col]):
                return 0
            if (i, j) in visited:
                return 1
            visited.add((i, j))
            border = all(dfs(x, y) for x, y in [(i+1, j), (i-1, j), (i, j+1), (i, j-1)])
            if border:
                grid[i][j] = color
            return border

        visited = set()
        dfs(row, col)
        return grid
class Solution:
    def colorBorder(self, grid: List[List[int]], row: int, col: int, color: int) -> List[List[int]]:
        def dfs(i, j):
            if not (0 <= i < len(grid) and 0 <= j < len(grid[0])) or grid[i][j] != grid[row][col]:
                return 0
            if (i, j) in visited:
                return 1
            visited.add((i, j))
            if all(dfs(i + x, j + y) for x, y in [(0, 1), (0, -1), (1, 0), (-1, 0)]):
                if any(grid[i + x][j + y] != grid[row][col] for x, y in [(0, 1), (0, -1), (1, 0), (-1, 0)]):
                    return 1
            return 0

        visited = set()
        dfs(row, col)
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if (i, j) in visited and any(grid[i + x][j + y] != grid[row][col] for x, y in [(0, 1), (0, -1), (1, 0), (-1, 0)]):
                    grid[i][j] = color
        return grid
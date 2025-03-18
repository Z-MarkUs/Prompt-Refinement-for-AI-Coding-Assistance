class Solution:
    def containsCycle(self, grid: List[List[str]]) -> bool:
        def dfs(row, col, prev_row, prev_col, visited):
            if row < 0 or row >= len(grid) or col < 0 or col >= len(grid[0]) or grid[row][col] != grid[prev_row][prev_col]:
                return False
            if (row, col) in visited:
                return True
            visited.add((row, col))
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                if (row + dr, col + dc) != (prev_row, prev_col):
                    if dfs(row + dr, col + dc, row, col, visited):
                        return True
            visited.remove((row, col))
            return False
        
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if (i, j) not in visited:
                    if dfs(i, j, -1, -1, set()):
                        return True
        return False
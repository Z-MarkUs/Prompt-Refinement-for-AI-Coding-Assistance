from typing import List

class Solution:
    def numEnclaves(self, grid: List[List[int]]) -> int:
        def dfs(i, j):
            if 0 <= i < len(grid) and 0 <= j < len(grid[0]) and grid[i][j] == 1:
                grid[i][j] = -1
                dfs(i+1, j)
                dfs(i-1, j)
                dfs(i, j+1)
                dfs(i, j-1)
        
        for i in range(len(grid)):
            dfs(i, 0)
            dfs(i, len(grid[0])-1)
        
        for j in range(len(grid[0])):
            dfs(0, j)
            dfs(len(grid)-1, j)
        
        return sum(cell == 1 for row in grid for cell in row)

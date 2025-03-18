from typing import List

class Solution:
    def containsCycle(self, grid: List[List[str]]) -> bool:
        def dfs(row, col, parent_row, parent_col, path_length):
            if visited[row][col]:
                return path_length - path_length_map[(row, col)] >= 4
            
            visited[row][col] = True
            path_length_map[(row, col)] = path_length
            
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < m and 0 <= new_col < n and grid[new_row][new_col] == grid[row][col] and (new_row != parent_row or new_col != parent_col):
                    if dfs(new_row, new_col, row, col, path_length + 1):
                        return True
            
            return False
        
        m, n = len(grid), len(grid[0])
        visited = [[False for _ in range(n)] for _ in range(m)]
        path_length_map = {}
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for i in range(m):
            for j in range(n):
                if not visited[i][j]:
                    if dfs(i, j, -1, -1, 1):
                        return True
        
        return False

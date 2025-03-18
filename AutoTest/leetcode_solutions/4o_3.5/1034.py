class Solution:
    def colorBorder(self, grid: List[List[int]], row: int, col: int, color: int) -> List[List[int]]:
        def dfs(r, c):
            pass
        
        original_color = grid[row][col]
        visited = set()
        borders = set()
        
        dfs(row, col)
        
        for r, c in borders:
            grid[r][c] = color
        
        return grid
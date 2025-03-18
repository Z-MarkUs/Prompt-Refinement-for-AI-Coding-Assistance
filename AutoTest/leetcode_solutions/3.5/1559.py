class Solution:
    def containsCycle(self, grid: List[List[str]]) -> bool:
        def dfs(x, y, prev_x, prev_y, visited):
            if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]) or grid[x][y] != grid[prev_x][prev_y]:
                return False
            if (x, y) in visited and len(visited) >= 4:
                return True
            if (x, y) in visited:
                return False
            visited.add((x, y))
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in directions:
                if dfs(x+dx, y+dy, x, y, visited):
                    return True
            visited.remove((x, y))
            return False
        
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if dfs(i, j, i, j, set()):
                    return True
        return False
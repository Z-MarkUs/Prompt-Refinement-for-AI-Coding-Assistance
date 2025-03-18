class Solution:
    def numSubmat(self, mat: List[List[int]) -> int:
        m, n = len(mat), len(mat[0])
        count = 0
        dp = [[0] * n for _ in range(m)]
        
        for i in range(m):
            for j in range(n):
                if mat[i][j] == 1:
                    dp[i][j] = dp[i][j-1] + 1 if j > 0 else 1
        
        for i in range(m):
            for j in range(n):
                minWidth = float('inf')
                for k in range(i, -1, -1):
                    minWidth = min(minWidth, dp[k][j])
                    if minWidth == 0:
                        break
                    count += minWidth
        
        return count
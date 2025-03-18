class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        dp = [[0] * (len(target) + 1) for _ in range(len(source) + 1)]
        
        for i in range(1, len(source) + 1):
            dp[i][0] = i
        
        for j in range(1, len(target) + 1):
            dp[0][j] = float('inf')
        
        for i in range(1, len(source) + 1):
            for j in range(1, len(target) + 1):
                if source[i-1] == target[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = dp[i-1][j]
        
        return dp[len(source)][len(target)] + 1
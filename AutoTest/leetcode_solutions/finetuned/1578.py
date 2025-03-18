class Solution:
    def minCost(self, colors: str, neededTime: List[int]) -> int:
        n = len(colors)
        dp = [[0] * 26 for _ in range(n)]
        
        for i in range(1, n):
            for j in range(26):
                dp[i][j] = dp[i-1][j] + neededTime[i-1]
            
            for j in range(26):
                if ord(colors[i]) - ord('a') != j:
                    dp[i][ord(colors[i]) - ord('a')] = min(dp[i][ord(colors[i]) - ord('a')], dp[i-1][j])
        
        return min(dp[n-1])
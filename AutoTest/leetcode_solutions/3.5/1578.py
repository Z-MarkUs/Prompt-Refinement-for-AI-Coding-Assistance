from typing import List

class Solution:
    def minCost(self, colors: str, neededTime: List[int]) -> int:
        n = len(colors)
        dp = [[float('inf')] * 26 for _ in range(n + 1)]
        dp[0] = [0] * 26
        for i in range(1, n + 1):
            color = ord(colors[i - 1]) - ord('a')
            for j in range(26):
                if j == color:
                    dp[i][j] = min(dp[i - 1][:j] + dp[i - 1][j + 1:]) + neededTime[i - 1]
                else:
                    dp[i][j] = dp[i - 1][j]
        return min(dp[n])
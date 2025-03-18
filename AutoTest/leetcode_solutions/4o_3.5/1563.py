from typing import List

class Solution:
    def stoneGameV(self, stoneValue: List[int]) -> int:
        n = len(stoneValue)
        prefix_sum = [0] * (n + 1)
        for i in range(n):
            prefix_sum[i + 1] = prefix_sum[i] + stoneValue[i]
        
        dp = [[0] * n for _ in range(n)]
        
        def stoneSum(i, j):
            return prefix_sum[j + 1] - prefix_sum[i]
        
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                for k in range(i, j):
                    left_sum = stoneSum(i, k)
                    right_sum = stoneSum(k + 1, j)
                    
                    if left_sum < right_sum:
                        dp[i][j] = max(dp[i][j], left_sum + dp[i][k])
                    elif left_sum > right_sum:
                        dp[i][j] = max(dp[i][j], right_sum + dp[k + 1][j])
                    else:
                        dp[i][j] = max(dp[i][j], left_sum + max(dp[i][k], dp[k + 1][j]))
        
        return dp[0][n - 1]

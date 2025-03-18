class Solution:
    def minDays(self, n: int) -> int:
        if n <= 1:
            return n
        
        dp = {}
        dp[0], dp[1] = 0, 1
        
        def dfs(n):
            if n in dp:
                return dp[n]
            
            dp[n] = 1 + min(n % 2 + dfs(n // 2), n % 3 + dfs(n // 3))
            return dp[n]
        
        return dfs(n)
class Solution:
    def countRoutes(self, locations: List[int], start: int, finish: int, fuel: int) -> int:
        MOD = 10**9 + 7
        n = len(locations)
        dp = [[0] * (fuel + 1) for _ in range(n)]
        
        dp[finish][0] = 1
        
        for f in range(fuel + 1):
            for i in range(n):
                for j in range(n):
                    cost = abs(locations[i] - locations[j])
                    if i != j and f >= cost:
                        dp[i][f] = (dp[i][f] + dp[j][f - cost]) % MOD
        
        return dp[start][fuel] % MOD
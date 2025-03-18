class Solution:
    def countRoutes(self, locations: List[int], start: int, finish: int, fuel: int) -> int:
        MOD = 10**9 + 7
        n = len(locations)
        dp = [[0] * n for _ in range(fuel + 1)]
        
        for f in range(fuel + 1):
            dp[f][start] = 1
        
        for f in range(fuel):
            for i in range(n):
                for j in range(n):
                    if i != j and f + abs(locations[i] - locations[j]) <= fuel:
                        dp[f + abs(locations[i] - locations[j])][j] += dp[f][i]
                        dp[f + abs(locations[i] - locations[j])][j] %= MOD
        
        return sum(dp[fuel][i] for i in range(n)) % MOD
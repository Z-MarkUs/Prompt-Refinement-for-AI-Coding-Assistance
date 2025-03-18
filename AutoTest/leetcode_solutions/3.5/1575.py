class Solution:
    def countRoutes(self, locations: List[int], start: int, finish: int, fuel: int) -> int:
        MOD = 10**9 + 7
        n = len(locations)
        dp = [[0] * (fuel + 1) for _ in range(n)]
        
        dp[start][fuel] = 1
        
        for f in range(fuel, -1, -1):
            for i in range(n):
                for j in range(n):
                    if i != j:
                        dist = abs(locations[i] - locations[j])
                        if f >= dist:
                            dp[j][f - dist] = (dp[j][f - dist] + dp[i][f]) % MOD
        
        return sum(dp[finish]) % MOD
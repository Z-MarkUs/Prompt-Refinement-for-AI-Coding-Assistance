class Solution:
    def stoneGameV(self, stoneValue: List[int]) -> int:
        n = len(stoneValue)
        prefix_sum = [0] * (n + 1)
        for i in range(n):
            prefix_sum[i + 1] = prefix_sum[i] + stoneValue[i]
        
        @lru_cache(None)
        def dp(i, j):
            if i == j:
                return 0
            res = 0
            for k in range(i + 1, j + 1):
                left_sum = prefix_sum[k] - prefix_sum[i]
                right_sum = prefix_sum[j] - prefix_sum[k]
                if left_sum < right_sum:
                    res = max(res, left_sum + dp(i, k - 1))
                elif left_sum > right_sum:
                    res = max(res, right_sum + dp(k, j))
                else:
                    res = max(res, left_sum + max(dp(i, k - 1), dp(k, j)))
            return res
        
        return dp(0, n - 1)
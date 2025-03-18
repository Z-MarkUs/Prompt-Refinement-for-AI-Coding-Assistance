class Solution:
    def stoneGameV(self, stoneValue: List[int]) -> int:
        n = len(stoneValue)
        prefix_sum = [0] * (n + 1)
        for i in range(n):
            prefix_sum[i + 1] = prefix_sum[i] + stoneValue[i]
        
        @lru_cache(None)
        def dp(left, right):
            if left == right:
                return 0
            
            result = 0
            for mid in range(left, right):
                sum_left = prefix_sum[mid + 1] - prefix_sum[left]
                sum_right = prefix_sum[right + 1] - prefix_sum[mid + 1]
                
                if sum_left < sum_right:
                    result = max(result, sum_left + dp(left, mid))
                elif sum_left > sum_right:
                    result = max(result, sum_right + dp(mid + 1, right))
                else:
                    result = max(result, sum_left + max(dp(left, mid), dp(mid + 1, right)))
            
            return result
        
        return dp(0, n - 1)
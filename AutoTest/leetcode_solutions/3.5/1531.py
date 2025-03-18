class Solution:
    def getLengthOfOptimalCompression(self, s: str, k: int) -> int:
        n = len(s)
        dp = [[[-1] * (k + 1) for _ in range(26)] for _ in range(n)]

        def dfs(i, prev, cnt):
            if cnt > k:
                return float('inf')
            if i == n:
                return 0
            if dp[i][prev][cnt] != -1:
                return dp[i][prev][cnt]

            # delete current character
            ans = dfs(i + 1, prev, cnt + 1)

            # keep current character
            add = 1 if cnt > 0 else 0
            if s[i] == prev:
                add = min(1, add)
            else:
                prev = s[i]

            ans = min(ans, add + dfs(i + 1, prev, cnt))

            # compress current character
            for j in range(1, 27):
                if j == prev:
                    continue
                if j == s[i]:
                    ans = min(ans, 1 + dfs(i + 1, j, cnt))
                else:
                    ans = min(ans, 1 + dfs(i + 1, j, cnt + 1))

            dp[i][prev][cnt] = ans
            return ans

        return dfs(0, -1, 0)
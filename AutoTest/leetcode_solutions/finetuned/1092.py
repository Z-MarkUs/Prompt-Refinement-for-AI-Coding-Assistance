class Solution:
    def shortestCommonSupersequence(self, str1: str, str2: str) -> str:
        m, n = len(str1), len(str2)
        dp = [["" for _ in range(n + 1)] for _ in range(m + 1)
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + str1[i - 1]
                else:
                    if len(dp[i - 1][j]) > len(dp[i][j - 1]):
                        dp[i][j] = dp[i - 1][j]
                    else:
                        dp[i][j] = dp[i][j - 1]
        
        lcs = dp[m][n]
        result = ""
        i, j = 0, 0
        for char in lcs:
            while str1[i] != char:
                result += str1[i]
                i += 1
            while str2[j] != char:
                result += str2[j]
                j += 1
            result += char
            i += 1
            j += 1
        
        result += str1[i:] + str2[j:]
        
        return result
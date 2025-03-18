class Solution:
    def longestRepeatingSubstring(self, s: str) -> int:
        def search(L: int) -> int:
            MOD = 2**63 - 1
            BASE = 26
            hashVal = 0
            baseL = pow(BASE, L, MOD)
            seen = set()
            for i in range(len(s) - L + 1):
                if i == 0:
                    for j in range(L):
                        hashVal = (hashVal * BASE + ord(s[j])) % MOD
                else:
                    hashVal = (hashVal * BASE - ord(s[i - 1]) * baseL + ord(s[i + L - 1])) % MOD
                if hashVal in seen:
                    return i
                seen.add(hashVal)
            return -1

        left, right = 1, len(s)
        while left < right:
            mid = (left + right + 1) // 2
            if search(mid) != -1:
                left = mid
            else:
                right = mid - 1
        return left - 1
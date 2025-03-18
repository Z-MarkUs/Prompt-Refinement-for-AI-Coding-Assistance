class Solution:
    def longestRepeatingSubstring(self, s: str) -> int:
        def search(L, n):
            seen = set()
            base = 26
            mod = 2**63 - 1
            hash_val = 0
            for i in range(L):
                hash_val = (hash_val * base + ord(s[i])) % mod
            seen.add(hash_val)
            baseL = pow(base, L, mod)
            for start in range(1, n - L + 1):
                hash_val = (hash_val * base - ord(s[start - 1]) * baseL + ord(s[start + L - 1])) % mod
                if hash_val in seen:
                    return start
                seen.add(hash_val)
            return -1
        
        n = len(s)
        left, right = 1, n
        while left <= right:
            L = left + (right - left) // 2
            if search(L, n) != -1:
                left = L + 1
            else:
                right = L - 1
        return left - 1
class Solution:
    def longestDupSubstring(self, s: str) -> str:
        def search(L, n, A, modulus):
            h = 0
            for i in range(L):
                h = (h * A + nums[i]) % modulus
            seen = {h}
            aL = pow(A, L, modulus)
            for start in range(1, n - L + 1):
                h = (h * A - nums[start - 1] * aL + nums[start + L - 1]) % modulus
                if h in seen:
                    return start
                seen.add(h)
            return -1

        n = len(s)
        nums = [ord(c) - ord('a') for c in s]
        A = 26
        modulus = 2**63 - 1

        left, right = 1, n
        while left < right:
            L = left + (right - left) // 2
            if search(L, n, A, modulus) != -1:
                left = L + 1
            else:
                right = L

        start = search(left - 1, n, A, modulus)
        return s[start:start + left - 1] if start != -1 else ""
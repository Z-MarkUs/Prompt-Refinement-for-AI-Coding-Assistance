class Solution:
    def longestAwesome(self, s: str) -> int:
        freq = {0: -1}
        mask = 0
        res = 0
        
        for i, c in enumerate(s):
            mask ^= 1 << int(c)
            if mask in freq:
                res = max(res, i - freq[mask])
            for j in range(10):
                new_mask = mask ^ (1 << j)
                if new_mask in freq:
                    res = max(res, i - freq[new_mask])
            if mask not in freq:
                freq[mask] = i
        
        return res
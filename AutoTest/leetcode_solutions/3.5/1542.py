class Solution:
    def longestAwesome(self, s: str) -> int:
        count = {0: -1}
        mask = 0
        res = 0
        
        for i, c in enumerate(s):
            mask ^= 1 << int(c)
            if mask in count:
                res = max(res, i - count[mask])
            for j in range(10):
                new_mask = mask ^ (1 << j)
                if new_mask in count:
                    res = max(res, i - count[new_mask])
            if mask not in count:
                count[mask] = i
        
        return res
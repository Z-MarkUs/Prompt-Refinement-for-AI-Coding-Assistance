class Solution:
    def confusingNumberII(self, n: int) -> int:
        def dfs(num, rotation, digit_map):
            nonlocal count
            if num != rotation:
                count += 1
            for d, r in digit_map.items():
                if num == 0 and d == 0:
                    continue
                if num * 10 + d <= n:
                    dfs(num * 10 + d, r * rotation, digit_map)
        
        count = 0
        digit_map = {0: 0, 1: 1, 6: 9, 8: 8, 9: 6}
        for d in [1, 6, 8, 9]:
            dfs(d, digit_map[d], digit_map)
        
        return count
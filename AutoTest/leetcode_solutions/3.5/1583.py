from typing import List

class Solution:
    def unhappyFriends(self, n: int, preferences: List[List[int]], pairs: List[List[int]]) -> int:
        def is_unhappy(x, y):
            return preferences[x].index(y) < preferences[x].index(pairs[x][1])

        pair_dict = {x: y for x, y in pairs}
        unhappy_count = 0

        for x in range(n):
            for y in preferences[x][:preferences[x].index(pair_dict[x])]:
                if is_unhappy(x, y) and is_unhappy(y, x):
                    unhappy_count += 1
                    break

        return unhappy_count
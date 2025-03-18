class Solution:
    def unhappyFriends(self, n: int, preferences: List[List[int]], pairs: List[List[int]]) -> int:
        def is_unhappy(x, y):
            return preferences[x].index(y) < preferences[x].index(pairs[x]) and preferences[y].index(x) < preferences[y].index(pairs[y])
        
        unhappy_count = 0
        for i in range(n):
            for j in range(n):
                if i != j and pairs[i] != j and is_unhappy(i, j):
                    unhappy_count += 1
                    break
        
        return unhappy_count
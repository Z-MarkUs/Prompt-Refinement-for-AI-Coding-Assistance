class Solution:
    def unhappyFriends(self, n: int, preferences: List[List[int]], pairs: List[List[int]]) -> int:
        pairings = {}
        for pair in pairs:
            pairings[pair[0]] = pair[1]
            pairings[pair[1]] = pair[0]
        
        unhappy_count = 0
        for x in range(n):
            y = preferences[x][0]
            if preferences[y].index(x) < preferences[y].index(pairings[y]):
                unhappy_count += 1
        
        return unhappy_count
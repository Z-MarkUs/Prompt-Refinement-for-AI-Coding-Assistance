from typing import List

class Solution:
    def mostVisited(self, n: int, rounds: List[int]) -> List[int]:
        visited = [0] * n
        start = rounds[0]
        end = rounds[-1]
        
        for i in range(len(rounds) - 1):
            current = rounds[i]
            next_sector = rounds[i + 1]
            while current != next_sector:
                visited[current - 1] += 1
                current = (current % n) + 1
        
        visited[end - 1] += 1
        
        max_visits = max(visited)
        result = [i + 1 for i in range(n) if visited[i] == max_visits]
        
        return result
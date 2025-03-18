from typing import List

class Solution:
    def leadsToDestination(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        graph = {i: [] for i in range(n)}
        for edge in edges:
            graph[edge[0]].append(edge[1])
        
        def dfs(node):
            if node == destination:
                return len(graph[node]) == 0
            if len(graph[node]) == 0:
                return False
            for neighbor in graph[node]:
                if not dfs(neighbor):
                    return False
            graph[node] = []
            return True
        
        return dfs(source)
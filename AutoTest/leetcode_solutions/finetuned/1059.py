class Solution:
    def leadsToDestination(self, n: int, edges: List[List[int]], source: int, destination: int) -> bool:
        def dfs(node):
            if visited[node] == 1:
                return False
            if visited[node] == 2:
                return True
            
            visited[node] = 1
            if node not in graph:
                visited[node] = 2
                return True
            
            for neighbor in graph[node]:
                if not dfs(neighbor):
                    return False
            
            visited[node] = 2
            return True
        
        graph = defaultdict(list)
        for edge in edges:
            graph[edge[0]].append(edge[1])
        
        visited = [0] * n
        return dfs(source)
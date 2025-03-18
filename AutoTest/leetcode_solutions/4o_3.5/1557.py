class Solution:
    def findSmallestSetOfVertices(self, n: int, edges: List[List[int]]) -> List[int]:
        indegree = [0] * n
        for edge in edges:
            indegree[edge[1]] += 1
        
        source_set = []
        for i in range(n):
            if indegree[i] == 0:
                source_set.append(i)
        
        return source_set
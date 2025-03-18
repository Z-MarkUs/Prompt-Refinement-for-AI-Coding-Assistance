from typing import List

class Solution:
    def minCostConnectPoints(self, points: List[List[int]]) -> int:
        def find(parent, x):
            if parent[x] != x:
                parent[x] = find(parent, parent[x])
            return parent[x]
        
        def union(parent, rank, x, y):
            root_x = find(parent, x)
            root_y = find(parent, y)
            if root_x != root_y:
                if rank[root_x] > rank[root_y]:
                    parent[root_y] = root_x
                elif rank[root_x] < rank[root_y]:
                    parent[root_x] = root_y
                else:
                    parent[root_y] = root_x
                    rank[root_x] += 1
        
        n = len(points)
        edges = []
        for i in range(n):
            for j in range(i+1, n):
                cost = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
                edges.append((cost, i, j))
        
        edges.sort()
        parent = [i for i in range(n)]
        rank = [0] * n
        min_cost = 0
        num_edges = 0
        
        for cost, x, y in edges:
            if find(parent, x) != find(parent, y):
                union(parent, rank, x, y)
                min_cost += cost
                num_edges += 1
                if num_edges == n - 1:
                    break
        
        return min_cost
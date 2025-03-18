class Solution:
    def minCostConnectPoints(self, points: List[List[int]]) -> int:
        def manhattan_distance(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        
        def find(parent, i):
            if parent[i] == i:
                return i
            return find(parent, parent[i])
        
        def union(parent, rank, x, y):
            x_root = find(parent, x)
            y_root = find(parent, y)
            
            if rank[x_root] < rank[y_root]:
                parent[x_root] = y_root
            elif rank[x_root] > rank[y_root]:
                parent[y_root] = x_root
            else:
                parent[y_root] = x_root
                rank[x_root] += 1
        
        edges = []
        n = len(points)
        for i in range(n):
            for j in range(i+1, n):
                edges.append((manhattan_distance(points[i], points[j]), i, j))
        
        edges.sort()
        
        parent = [i for i in range(n)]
        rank = [0] * n
        min_cost = 0
        
        for edge in edges:
            cost, x, y = edge
            if find(parent, x) != find(parent, y):
                min_cost += cost
                union(parent, rank, x, y)
        
        return min_cost
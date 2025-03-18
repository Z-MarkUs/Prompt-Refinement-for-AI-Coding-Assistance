from typing import List

class Solution:
    def maxNumEdgesToRemove(self, n: int, edges: List[List[int]]) -> int:
        def find(parent, x):
            if parent[x] != x:
                parent[x] = find(parent, parent[x])
            return parent[x]

        def union(parent, rank, x, y):
            root_x = find(parent, x)
            root_y = find(parent, y)

            if root_x == root_y:
                return False

            if rank[root_x] < rank[root_y]:
                parent[root_x] = root_y
            elif rank[root_x] > rank[root_y]:
                parent[root_y] = root_x
            else:
                parent[root_y] = root_x
                rank[root_x] += 1

            return True

        edges.sort(key=lambda x: -x[0])

        parent = [i for i in range(n + 1)]
        rank = [0] * (n + 1)

        alice_edges = 0
        bob_edges = 0
        common_edges = 0

        for edge_type, node1, node2 in edges:
            if edge_type == 3:
                if union(parent, rank, node1, node2):
                    alice_edges += 1
                    bob_edges += 1
                    common_edges += 1
            elif edge_type == 1:
                if union(parent, rank, node1, node2):
                    alice_edges += 1
            elif edge_type == 2:
                if union(parent, rank, node1, node2):
                    bob_edges += 1

        if alice_edges + bob_edges == n - 1:
            return len(edges) - (n - 1 - common_edges)
        else:
            return -1
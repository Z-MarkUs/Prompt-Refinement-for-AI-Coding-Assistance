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

        edges.sort(reverse=True)  # Sort edges in descending order

        parent_a = [i for i in range(n + 1)]  # Parent array for Alice
        parent_b = [i for i in range(n + 1)]  # Parent array for Bob
        rank_a = [0] * (n + 1)  # Rank array for Alice
        rank_b = [0] * (n + 1)  # Rank array for Bob

        count = 0  # Count of removable edges

        for edge_type, node1, node2 in edges:
            if edge_type == 3:
                if union(parent_a, rank_a, node1, node2) and union(parent_b, rank_b, node1, node2):
                    count += 1
            elif edge_type == 1:
                if union(parent_a, rank_a, node1, node2):
                    count += 1
            elif edge_type == 2:
                if union(parent_b, rank_b, node1, node2):
                    count += 1

        if len(set(find(parent_a, i) for i in range(1, n + 1))) == 1 and len(set(find(parent_b, i) for i in range(1, n + 1))) == 1:
            return len(edges) - count
        else:
            return -1
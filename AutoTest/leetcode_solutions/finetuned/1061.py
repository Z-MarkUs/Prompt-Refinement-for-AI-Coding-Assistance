class Solution:
    def smallestEquivalentString(self, s1: str, s2: str, baseStr: str) -> str:
        def find(parent, x):
            if parent[x] != x:
                parent[x] = find(parent, parent[x])
            return parent[x]

        def union(parent, rank, x, y):
            rootX = find(parent, x)
            rootY = find(parent, y)
            if rootX != rootY:
                if rank[rootX] > rank[rootY]:
                    parent[rootY] = rootX
                elif rank[rootX] < rank[rootY]:
                    parent[rootX] = rootY
                else:
                    parent[rootY] = rootX
                    rank[rootX] += 1

        parent = {}
        rank = {}
        for i in range(26):
            parent[chr(ord('a') + i)] = chr(ord('a') + i)
            rank[chr(ord('a') + i)] = 0

        for i in range(len(s1)):
            union(parent, rank, s1[i], s2[i])

        result = ""
        for char in baseStr:
            result += find(parent, char)

        return result
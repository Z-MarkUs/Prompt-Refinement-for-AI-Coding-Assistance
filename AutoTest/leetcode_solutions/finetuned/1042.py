class Solution:
    def gardenNoAdj(self, n: int, paths: List[List[int]]) -> List[int]:
        # Initialize a list to store the flower types for each garden
        flowers = [0] * n
        
        # Create a graph representation where each garden is a node and paths are edges
        graph = [[] for _ in range(n)]
        for x, y in paths:
            graph[x - 1].append(y - 1)
            graph[y - 1].append(x - 1)
        
        # Assign flower types to gardens
        for i in range(n):
            neighbor_flowers = set(flowers[j] for j in graph[i])
            for flower in range(1, 5):
                if flower not in neighbor_flowers:
                    flowers[i] = flower
                    break
        
        return flowers
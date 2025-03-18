class Solution:
    def gardenNoAdj(self, n: int, paths: List[List[int]]) -> List[int]:
        graph = defaultdict(list)
        for path in paths:
            graph[path[0]].append(path[1])
            graph[path[1]].append(path[0])
        
        flowers = [0] * n
        for i in range(n):
            neighbor_flowers = set(flowers[node-1] for node in graph[i+1])
            for flower in range(1, 5):
                if flower not in neighbor_flowers:
                    flowers[i] = flower
                    break
        
        return flowers
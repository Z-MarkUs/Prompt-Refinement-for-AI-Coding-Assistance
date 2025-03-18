class Solution:
    def maxProbability(self, n: int, edges: List[List[int]], succProb: List[float], start_node: int, end_node: int) -> float:
        graph = defaultdict(list)
        for i, (u, v) in enumerate(edges):
            graph[u].append((v, succProb[i]))
            graph[v].append((u, succProb[i]))
        
        pq = [(-1, start_node)]
        heapq.heapify(pq)
        probs = [0] * n
        probs[start_node] = 1
        
        while pq:
            prob, node = heapq.heappop(pq)
            if node == end_node:
                return -prob
            for nei, nei_prob in graph[node]:
                if -prob * nei_prob > probs[nei]:
                    probs[nei] = -prob * nei_prob
                    heapq.heappush(pq, (-probs[nei], nei))
        
        return 0.0
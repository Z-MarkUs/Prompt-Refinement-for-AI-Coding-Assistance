from typing import List

class Solution:
    def maxProbability(self, n: int, edges: List[List[int]], succProb: List[float], start_node: int, end_node: int) -> float:
        graph = {}
        for i in range(len(edges)):
            if edges[i][0] not in graph:
                graph[edges[i][0]] = {}
            if edges[i][1] not in graph:
                graph[edges[i][1]] = {}
            graph[edges[i][0]][edges[i][1]] = succProb[i]
            graph[edges[i][1]][edges[i][0]] = succProb[i]
        
        visited = [False] * n
        success_prob = [0.0] * n
        success_prob[start_node] = 1.0
        
        for _ in range(n):
            max_prob = -1
            max_node = -1
            for i in range(n):
                if not visited[i] and success_prob[i] > max_prob:
                    max_prob = success_prob[i]
                    max_node = i
            if max_node == -1:
                break
            visited[max_node] = True
            for neighbor, prob in graph.get(max_node, {}).items():
                if not visited[neighbor] and success_prob[max_node] * prob > success_prob[neighbor]:
                    success_prob[neighbor] = success_prob[max_node] * prob
        
        return success_prob[end_node]
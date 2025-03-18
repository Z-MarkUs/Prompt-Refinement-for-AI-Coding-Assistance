class Solution:
    def countSubTrees(self, n: int, edges: List[List[int]], labels: str) -> List[int]:
        def dfs(node, parent):
            count = [0] * 26
            label = ord(labels[node]) - ord('a')
            count[label] = 1
            for child in graph[node]:
                if child == parent:
                    continue
                child_count = dfs(child, node)
                for i in range(26):
                    count[i] += child_count[i]
            result[node] = count[label]
            return count
        
        graph = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)
        
        result = [0] * n
        dfs(0, -1)
        
        return result
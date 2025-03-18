from collections import defaultdict

class Solution:
    def countSubTrees(self, n: int, edges: List[List[int]], labels: str) -> List[int]:
        graph = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)
        
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
            ans[node] = count[label]
            return count
        
        ans = [0] * n
        dfs(0, -1)
        return ans
from typing import List, Optional

# Definition for a Node.
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List['Node']] = None):
        self.val = val
        self.children = children if children is not None else []

class Solution:
    def diameter(self, root: 'Node') -> int:
        def dfs(node):
            nonlocal diameter
            if not node:
                return 0
            max_depth1, max_depth2 = 0, 0
            for child in node.children:
                depth = dfs(child)
                if depth > max_depth1:
                    max_depth1, max_depth2 = depth, max_depth1
                elif depth > max_depth2:
                    max_depth2 = depth
            diameter = max(diameter, max_depth1 + max_depth2)
            return max_depth1 + 1
        
        diameter = 0
        dfs(root)
        return diameter
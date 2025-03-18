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
            if not node.children:
                return 0
            
            max_height1 = max_height2 = 0
            for child in node.children:
                height = dfs(child) + 1
                if height > max_height1:
                    max_height1, max_height2 = height, max_height1
                elif height > max_height2:
                    max_height2 = height
            
            diameter = max(diameter, max_height1 + max_height2)
            return max_height1
        
        diameter = 0
        if root:
            dfs(root)
        
        return diameter

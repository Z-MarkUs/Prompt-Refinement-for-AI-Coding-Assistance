from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def recoverFromPreorder(self, traversal: str) -> Optional[TreeNode]:
        def helper(nodes, level):
            if not nodes or not nodes[0]:
                return None
            
            val = nodes[0]
            nodes.pop(0)
            
            left_nodes = []
            right_nodes = []
            for node in nodes:
                if node[1] == level + 1:
                    left_nodes.append(node)
                elif node[1] == level + 2:
                    right_nodes.append(node)
                else:
                    break
            
            node = TreeNode(val)
            node.left = helper(left_nodes, level + 1)
            node.right = helper(right_nodes, level + 1)
            
            return node
        
        nodes = [(int(val), val.count('-')) for val in traversal.split('-')]
        return helper(nodes, 0)

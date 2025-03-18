from typing import List, Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def bstFromPreorder(self, preorder: List[int]) -> Optional[TreeNode]:
        def construct_bst(preorder, start, end):
            if start > end:
                return None
            
            root_val = preorder[start]
            root = TreeNode(root_val)
            
            if start == end:
                return root
            
            right_start = end + 1
            for i in range(start + 1, end + 1):
                if preorder[i] > root_val:
                    right_start = i
                    break
            
            root.left = construct_bst(preorder, start + 1, right_start - 1)
            root.right = construct_bst(preorder, right_start, end)
            
            return root
        
        return construct_bst(preorder, 0, len(preorder) - 1)
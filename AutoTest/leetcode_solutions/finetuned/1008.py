class Solution:
    def bstFromPreorder(self, preorder: List[int]) -> Optional[TreeNode]:
        def helper(lower, upper):
            nonlocal idx
            if idx == len(preorder):
                return None
            
            val = preorder[idx]
            if val < lower or val > upper:
                return None
            
            idx += 1
            root = TreeNode(val)
            root.left = helper(lower, val)
            root.right = helper(val, upper)
            return root
        
        idx = 0
        return helper(float('-inf'), float('inf'))
class Solution:
    def bstFromPreorder(self, preorder: List[int]) -> Optional[TreeNode]:
        def build_bst(preorder, lower, upper):
            if self.idx == len(preorder):
                return None
            
            val = preorder[self.idx]
            if val < lower or val > upper:
                return None
            
            self.idx += 1
            root = TreeNode(val)
            root.left = build_bst(preorder, lower, val)
            root.right = build_bst(preorder, val, upper)
            
            return root
        
        self.idx = 0
        return build_bst(preorder, float('-inf'), float('inf'))
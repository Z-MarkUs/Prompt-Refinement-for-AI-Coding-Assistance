class Solution:
    def bstToGst(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        def reverse_inorder(node, total):
            if not node:
                return total
            
            total = reverse_inorder(node.right, total)
            node.val += total
            total = node.val
            total = reverse_inorder(node.left, total)
            
            return total
        
        reverse_inorder(root, 0)
        
        return root
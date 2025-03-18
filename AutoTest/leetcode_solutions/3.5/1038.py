class Solution:
    def bstToGst(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        def dfs(node, total):
            if not node:
                return total
            
            node.val += dfs(node.right, total)
            return dfs(node.left, node.val)
        
        dfs(root, 0)
        return root
class Solution:
    def sumRootToLeaf(self, root: Optional[TreeNode]) -> int:
        def dfs(node, val):
            if not node:
                return 0
            val = (val << 1) + node.val
            if not node.left and not node.right:
                return val
            return (dfs(node.left, val) + dfs(node.right, val)) % (10**9 + 7)
        
        return dfs(root, 0)
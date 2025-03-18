class Solution:
    def diameter(self, root: 'Node') -> int:
        def dfs(node):
            if not node:
                return 0, 0
            
            max_height1, max_height2, max_diameter = 0, 0, 0
            for child in node.children:
                height, diameter = dfs(child)
                if height > max_height1:
                    max_height2 = max_height1
                    max_height1 = height
                elif height > max_height2:
                    max_height2 = height
                max_diameter = max(max_diameter, diameter)
            
            return max_height1 + 1, max(max_diameter, max_height1 + max_height2)
        
        _, diameter = dfs(root)
        return diameter
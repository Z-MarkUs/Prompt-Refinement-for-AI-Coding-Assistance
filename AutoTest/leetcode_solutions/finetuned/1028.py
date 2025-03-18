class Solution:
    def recoverFromPreorder(self, traversal: str) -> Optional[TreeNode]:
        def build_tree(nodes):
            if not nodes:
                return None
            root_val = nodes.pop(0)
            root = TreeNode(int(root_val))
            left_nodes, right_nodes = [], []
            for node in nodes:
                if node[0] == '-':
                    break
                left_nodes.append(node)
            for node in nodes[len(left_nodes):]:
                if node[0] == '-':
                    break
                right_nodes.append(node)
            root.left = build_tree(left_nodes)
            root.right = build_tree(right_nodes)
            return root
        
        nodes = traversal.split('-')
        return build_tree(nodes[1:])
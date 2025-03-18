class Solution:
    def moveSubTree(self, root: 'Node', p: 'Node', q: 'Node') -> 'Node':
        def find_node(node, target):
            if node == target:
                return node
            for child in node.children:
                result = find_node(child, target)
                if result:
                    return result
            return None
        
        def remove_node(node, target):
            for i, child in enumerate(node.children):
                if child == target:
                    del node.children[i]
                    return True
                if remove_node(child, target):
                    return True
            return False
        
        def add_node(node, target):
            target.children.append(node)
        
        if p == q:
            return root
        
        if find_node(p, q):
            return root
        
        remove_node(root, p)
        add_node(p, q)
        
        return root
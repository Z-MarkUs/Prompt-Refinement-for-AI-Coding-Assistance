class Solution:
    def moveSubTree(self, root: 'Node', p: 'Node', q: 'Node') -> 'Node':
        def find_node(node, target):
            if not node:
                return None
            if node == target:
                return node
            for child in node.children:
                found = find_node(child, target)
                if found:
                    return found
            return None
        
        def remove_node(node, target):
            if not node:
                return None
            if target in node.children:
                node.children.remove(target)
                return node
            for child in node.children:
                removed = remove_node(child, target)
                if removed:
                    return removed
            return None
        
        def add_node(node, target):
            if not node:
                return None
            if node == target:
                node.children.append(p)
                return node
            for child in node.children:
                added = add_node(child, target)
                if added:
                    return added
            return None
        
        if p == q:
            return root
        
        find_node(root, p)
        parent_p = remove_node(root, p)
        add_node(root, q)
        
        return root
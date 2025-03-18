class Solution:
    def findRoot(self, tree: List['Node']) -> 'Node':
        candidate_roots = set(tree)
        
        for node in tree:
            for child in node.children:
                if child in candidate_roots:
                    candidate_roots.remove(child)
        
        return candidate_roots.pop()
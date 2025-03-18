class Solution:
    def findRoot(self, tree: List['Node']) -> 'Node':
        nodes = set()
        for node in tree:
            nodes.add(node)
            for child in node.children:
                nodes.add(child)
        
        for node in nodes:
            if node not in nodes:
                return node
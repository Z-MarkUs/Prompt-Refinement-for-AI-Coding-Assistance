class Solution:
    def findSmallestSetOfVertices(self, n: int, edges: List[List[int]]) -> List[int]:
        # Create a set to store all destination nodes
        destinations = set()
        
        # Iterate through the edges to find all destination nodes
        for edge in edges:
            destinations.add(edge[1])
        
        # Find the source nodes by subtracting destinations from all nodes
        source_nodes = [i for i in range(n) if i not in destinations]
        
        return source_nodes
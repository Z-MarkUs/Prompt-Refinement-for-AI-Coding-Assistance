```python
from typing import List

class Solution:
    def assignBikes(self, workers: List[List[int]], bikes: List[List[int]]) -> List[int]:
        def manhattan_distance(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        
        distances = []
        for i, worker in enumerate(workers):
            for j, bike in enumerate(bikes):
                distance = manhattan_distance(worker, bike)
                distances.append((distance, i, j))
        
        distances.sort()
        
        result = [-1] * len(workers)
        bike_assigned = set()
        
        for distance, worker_idx, bike_idx in distances:
            if result[worker_idx] == -1 and bike_idx not in bike_assigned:
                result[worker_idx] = bike_idx
                bike_assigned.add(bike_idx)
        
        return result
```
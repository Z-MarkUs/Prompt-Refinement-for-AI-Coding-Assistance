class Solution:
    def assignBikes(self, workers: List[List[int]], bikes: List[List[int]]) -> List[int]:
        def manhattan_distance(worker, bike):
            return abs(worker[0] - bike[0]) + abs(worker[1] - bike[1])
        
        distances = []
        for i, worker in enumerate(workers):
            for j, bike in enumerate(bikes):
                distance = manhattan_distance(worker, bike)
                distances.append((distance, i, j))
        
        distances.sort()
        
        assigned = set()
        result = [-1] * len(workers)
        
        for distance, worker_idx, bike_idx in distances:
            if result[worker_idx] == -1 and bike_idx not in assigned:
                result[worker_idx] = bike_idx
                assigned.add(bike_idx)
        
        return result
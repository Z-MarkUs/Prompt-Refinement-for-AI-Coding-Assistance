class Solution:
    def rearrangeBarcodes(self, barcodes: List[int]) -> List[int]:
        # Count frequencies of each element
        freq = collections.Counter(barcodes)
        
        # Use a priority queue to manage elements by frequency
        pq = [(-f, num) for num, f in freq.items()]
        heapq.heapify(pq)
        
        res = []
        
        while len(pq) >= 2:
            f1, num1 = heapq.heappop(pq)
            f2, num2 = heapq.heappop(pq)
            
            res.extend([num1, num2])
            
            if f1 + 1 < 0:
                heapq.heappush(pq, (f1 + 1, num1))
            if f2 + 1 < 0:
                heapq.heappush(pq, (f2 + 1, num2))
        
        if pq:
            res.append(pq[0][1])
        
        return res
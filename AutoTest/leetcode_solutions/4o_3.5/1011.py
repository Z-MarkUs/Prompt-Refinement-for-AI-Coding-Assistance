from typing import List

class Solution:
    def shipWithinDays(self, weights: List[int], days: int) -> int:
        def feasible(capacity: int) -> bool:
            current_weight = 0
            required_days = 1
            
            for weight in weights:
                if current_weight + weight > capacity:
                    required_days += 1
                    current_weight = 0
                
                current_weight += weight
            
            return required_days <= days
        
        left, right = max(weights), sum(weights)
        
        while left < right:
            mid = left + (right - left) // 2
            
            if feasible(mid):
                right = mid
            else:
                left = mid + 1
        
        return left
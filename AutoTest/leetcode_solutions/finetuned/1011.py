class Solution:
    def shipWithinDays(self, weights: List[int], days: int) -> int:
        def can_ship_within_days(capacity):
            current_capacity = 0
            required_days = 1
            for weight in weights:
                if current_capacity + weight > capacity:
                    required_days += 1
                    current_capacity = 0
                current_capacity += weight
            return required_days <= days
        
        left = max(weights)
        right = sum(weights)
        
        while left < right:
            mid = left + (right - left) // 2
            if can_ship_within_days(mid):
                right = mid
            else:
                left = mid + 1
        
        return left
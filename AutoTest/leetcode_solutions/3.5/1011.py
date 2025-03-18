class Solution:
    def shipWithinDays(self, weights: List[int], days: int) -> int:
        def is_possible(capacity):
            curr_capacity = 0
            curr_days = 1
            for weight in weights:
                if curr_capacity + weight > capacity:
                    curr_days += 1
                    curr_capacity = 0
                curr_capacity += weight
            return curr_days <= days
        
        left, right = max(weights), sum(weights)
        while left < right:
            mid = left + (right - left) // 2
            if is_possible(mid):
                right = mid
            else:
                left = mid + 1
        return left
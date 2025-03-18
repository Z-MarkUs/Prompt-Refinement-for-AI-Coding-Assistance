class Solution:
    def maxDistance(self, position: List[int], m: int) -> int:
        def countBalls(min_dist):
            count = 1
            prev = position[0]
            for i in range(1, len(position)):
                if position[i] - prev >= min_dist:
                    count += 1
                    prev = position[i]
            return count
        
        position.sort()
        left, right = 0, position[-1] - position[0]
        
        while left < right:
            mid = (left + right + 1) // 2
            if countBalls(mid) >= m:
                left = mid
            else:
                right = mid - 1
        
        return left
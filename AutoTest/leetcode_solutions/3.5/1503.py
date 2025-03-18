class Solution:
    def getLastMoment(self, n: int, left: List[int], right: List[int]) -> int:
        max_time = 0
        for ant in left:
            max_time = max(max_time, ant)
        for ant in right:
            max_time = max(max_time, n - ant)
        return max_time
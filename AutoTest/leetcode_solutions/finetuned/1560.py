class Solution:
    def mostVisited(self, n: int, rounds: List[int]) -> List[int]:
        sector_visits = [0] * n
        for i in range(len(rounds) - 1):
            start = rounds[i]
            end = rounds[i + 1]
            if start <= end:
                for j in range(start, end):
                    sector_visits[(j - 1) % n] += 1
            else:
                for j in range(start, n + 1):
                    sector_visits[(j - 1) % n] += 1
                for j in range(1, end):
                    sector_visits[(j - 1) % n] += 1
        
        max_visits = max(sector_visits)
        result = [i + 1 for i in range(n) if sector_visits[i] == max_visits]
        
        return result
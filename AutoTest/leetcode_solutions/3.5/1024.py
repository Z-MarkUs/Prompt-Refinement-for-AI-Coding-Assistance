from typing import List

class Solution:
    def videoStitching(self, clips: List[List[int]], time: int) -> int:
        clips.sort()
        dp = [float('inf')] * (time + 1)
        dp[0] = 0
        
        for start, end in clips:
            for i in range(start, min(end, time) + 1):
                dp[i] = min(dp[i], dp[start] + 1)
        
        return dp[time] if dp[time] != float('inf') else -1
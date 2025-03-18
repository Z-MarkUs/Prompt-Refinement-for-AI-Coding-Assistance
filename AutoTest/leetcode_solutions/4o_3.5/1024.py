from typing import List

class Solution:
    def videoStitching(self, clips: List[List[int]], time: int) -> int:
        # Sort clips based on start time, then end time
        clips.sort(key=lambda x: (x[0], x[1]))
        
        # Initialize variables
        count = 0
        current_end = 0
        farthest_reachable = 0
        
        # Greedy approach to select clips
        for clip in clips:
            start, end = clip
            if start > farthest_reachable:
                return -1
            if start > current_end:
                count += 1
                current_end = farthest_reachable
            farthest_reachable = max(farthest_reachable, end)
            if farthest_reachable >= time:
                return count
        if farthest_reachable < time:
            return -1
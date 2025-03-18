class Solution:
    def videoStitching(self, clips: List[List[int]], time: int) -> int:
        clips.sort(key=lambda x: (x[0], x[1]))
        end_time = 0
        count = 0
        
        for clip in clips:
            if clip[0] <= end_time:
                end_time = max(end_time, clip[1])
                count += 1
                if end_time >= time:
                    return count
        
        return -1
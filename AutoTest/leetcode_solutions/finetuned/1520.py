class Solution:
    def maxNumOfSubstrings(self, s: str) -> List[str]:
        def merge_intervals(intervals):
            merged = []
            for interval in sorted(intervals, key=lambda x: x[0]):
                if not merged or merged[-1][1] < interval[0]:
                    merged.append(interval)
                else:
                    merged[-1][1] = max(merged[-1][1], interval[1])
            return merged
        
        char_to_interval = {c: [float('inf'), -1] for c in string.ascii_lowercase}
        for i, c in enumerate(s):
            char_to_interval[c][0] = min(char_to_interval[c][0], i)
            char_to_interval[c][1] = max(char_to_interval[c][1], i)
        
        intervals = list(char_to_interval.values())
        merged_intervals = merge_intervals(intervals)
        
        result = []
        prev_end = -1
        for start, end in merged_intervals:
            if start > prev_end:
                result.append(s[start:end+1])
                prev_end = end
        
        return result
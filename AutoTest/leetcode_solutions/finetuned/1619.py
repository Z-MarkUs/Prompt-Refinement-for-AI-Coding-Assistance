class Solution:
    def trimMean(self, arr: List[int]) -> float:
        arr.sort()
        trim_size = len(arr) // 20
        trimmed_arr = arr[trim_size:-trim_size]
        return round(sum(trimmed_arr) / len(trimmed_arr), 5)
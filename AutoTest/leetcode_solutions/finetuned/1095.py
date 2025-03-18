class Solution:
    def findInMountainArray(self, target: int, mountainArr: 'MountainArray') -> int:
        def find_peak(arr):
            left, right = 0, arr.length() - 1
            while left < right:
                mid = left + (right - left) // 2
                if arr.get(mid) < arr.get(mid + 1):
                    left = mid + 1
                else:
                    right = mid
            return left
        
        def binary_search_asc(arr, target, left, right):
            while left <= right:
                mid = left + (right - left) // 2
                mid_val = arr.get(mid)
                if mid_val == target:
                    return mid
                elif mid_val < target:
                    left = mid + 1
                else:
                    right = mid - 1
            return -1
        
        def binary_search_desc(arr, target, left, right):
            while left <= right:
                mid = left + (right - left) // 2
                mid_val = arr.get(mid)
                if mid_val == target:
                    return mid
                elif mid_val < target:
                    right = mid - 1
                else:
                    left = mid + 1
            return -1
        
        peak = find_peak(mountainArr)
        res = binary_search_asc(mountainArr, target, 0, peak)
        if res != -1:
            return res
        return binary_search_desc(mountainArr, target, peak + 1, mountainArr.length() - 1)
class Solution:
    def findInMountainArray(self, target: int, mountainArr: 'MountainArray') -> int:
        n = mountainArr.length()
        
        # Find peak index
        left, right = 0, n - 1
        while left < right:
            mid = left + (right - left) // 2
            if mountainArr.get(mid) < mountainArr.get(mid + 1):
                left = mid + 1
            else:
                right = mid
        
        peak = left
        
        # Binary search increasing part
        left, right = 0, peak
        while left <= right:
            mid = left + (right - left) // 2
            mid_val = mountainArr.get(mid)
            if mid_val == target:
                return mid
            elif mid_val < target:
                left = mid + 1
            else:
                right = mid - 1
        
        # Binary search decreasing part
        left, right = peak, n - 1
        while left <= right:
            mid = left + (right - left) // 2
            mid_val = mountainArr.get(mid)
            if mid_val == target:
                return mid
            elif mid_val < target:
                right = mid - 1
            else:
                left = mid + 1
        
        return -1
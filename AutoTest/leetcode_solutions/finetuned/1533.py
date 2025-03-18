class Solution:
    def getIndex(self, reader: 'ArrayReader') -> int:
        def binarySearch(left, right):
            if left == right:
                return left
            
            mid = left + (right - left) // 2
            length = reader.length()
            
            if (right - left) % 2 == 0:
                mid2 = mid + 1
                if reader.compareSub(left, mid, mid2, right) == 1:
                    return binarySearch(left, mid)
                else:
                    return binarySearch(mid2, right)
            else:
                if reader.compareSub(left, mid, mid, right) == 1:
                    return binarySearch(left, mid)
                else:
                    return binarySearch(mid + 1, right)
        
        return binarySearch(0, reader.length() - 1)
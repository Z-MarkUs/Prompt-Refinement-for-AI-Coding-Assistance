class Solution:
    def guessMajority(self, reader: 'ArrayReader') -> int:
        n = reader.length()
        
        def count_ones(start, end):
            return reader.query(start, end, start, end)
        
        def find_majority(start, end):
            if start == end:
                return start
            
            mid = (start + end) // 2
            left_count = count_ones(start, mid)
            right_count = count_ones(mid + 1, end)
            
            if left_count == right_count:
                return -1
            
            if left_count > right_count:
                return find_majority(start, mid)
            else:
                return find_majority(mid + 1, end)
        
        return find_majority(0, n - 1)
class Solution:
    def queryString(self, s: str, n: int) -> bool:
        binary_set = set()
        for i in range(1, n + 1):
            binary_set.add(bin(i)[2:])
        
        for binary_num in binary_set:
            if binary_num not in s:
                return False
        
        return True
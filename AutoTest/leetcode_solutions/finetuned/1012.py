class Solution:
    def numDupDigitsAtMostN(self, n: int) -> int:
        count = 0
        num = n + 1
        
        digits = []
        while num > 0:
            digits.insert(0, num % 10)
            num //= 10
        
        length = len(digits)
        
        def permuteUnique(index, used, num_count):
            if index == length:
                return 1 if num_count > 0 else 0
            
            result = 0
            for i in range(0 if index > 0 else 1, 10):
                if not used[i]:
                    new_used = used[:]
                    new_num_count = num_count
                    if new_used[i]:
                        new_num_count += 1
                    new_used[i] = True
                    result += permuteUnique(index + 1, new_used, new_num_count)
            
            return result
        
        for i in range(1, length):
            count += 9 * permuteUnique(0, [False] * 10, 0)
        
        used = [False] * 10
        num_count = 0
        for i in range(length):
            for j in range(0 if i > 0 else 1, digits[i]):
                if not used[j]:
                    new_used = used[:]
                    new_num_count = num_count
                    if new_used[j]:
                        new_num_count += 1
                    new_used[j] = True
                    count += permuteUnique(i + 1, new_used, new_num_count)
            
            if used[digits[i]]:
                break
            
            used[digits[i]] = True
            num_count += 1
        
        return n - count
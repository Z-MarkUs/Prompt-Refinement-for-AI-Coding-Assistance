class Solution:
    def numDupDigitsAtMostN(self, n: int) -> int:
        def factorial(n):
            if n == 0:
                return 1
            return n * factorial(n-1)
        
        def countNumbersWithUniqueDigits(n):
            if n == 0:
                return 1
            if n == 1:
                return 10
            count = 10
            unique_digits = 9
            available_digits = 9
            for i in range(2, n+1):
                unique_digits *= available_digits
                count += unique_digits
                available_digits -= 1
            return count
        
        def countNumbersWithRepeatedDigits(n):
            count = 0
            num_str = str(n)
            length = len(num_str)
            for i in range(1, length):
                count += 9 * factorial(9) // factorial(9-i)
            unique_digits_count = countNumbersWithUniqueDigits(length-1)
            num_set = set()
            for i, digit in enumerate(num_str):
                for j in range(int(digit)):
                    if j not in num_set:
                        count += 9 * factorial(9-len(num_set)) // factorial(9-len(num_set)-length+i)
                if digit in num_set:
                    break
                num_set.add(int(digit))
            return n - unique_digits_count + count
        
        return countNumbersWithRepeatedDigits(n)
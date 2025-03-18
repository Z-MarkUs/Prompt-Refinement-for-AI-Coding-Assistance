class Solution:
    def numPrimeArrangements(self, n: int) -> int:
        def is_prime(num):
            if num < 2:
                return False
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    return False
            return True
        
        def factorial(num):
            if num == 0:
                return 1
            return num * factorial(num - 1)
        
        prime_count = sum(1 for i in range(1, n + 1) if is_prime(i))
        non_prime_count = n - prime_count
        
        return (factorial(prime_count) * factorial(non_prime_count)) % (10**9 + 7)
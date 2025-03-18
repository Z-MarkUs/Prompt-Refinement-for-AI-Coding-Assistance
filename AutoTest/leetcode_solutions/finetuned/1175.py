class Solution:
    def numPrimeArrangements(self, n: int) -> int:
        def countPrimes(n):
            if n < 2:
                return 0
            primes = [True] * (n + 1)
            primes[0] = primes[1] = False
            p = 2
            while p * p <= n:
                if primes[p]:
                    for i in range(p * p, n + 1, p):
                        primes[i] = False
                p += 1
            return sum(primes)
        
        def factorial(n):
            result = 1
            for i in range(1, n + 1):
                result = (result * i) % (10**9 + 7)
            return result
        
        prime_count = countPrimes(n)
        non_prime_count = n - prime_count
        
        return (factorial(prime_count) * factorial(non_prime_count)) % (10**9 + 7)
class Solution:
    def numPrimeArrangements(self, n: int) -> int:
        def sieve_of_eratosthenes(limit):
            primes = []
            is_prime = [True] * (limit + 1)
            p = 2
            while p**2 <= limit:
                if is_prime[p]:
                    for i in range(p**2, limit + 1, p):
                        is_prime[i] = False
                p += 1
            for i in range(2, limit + 1):
                if is_prime[i]:
                    primes.append(i)
            return primes
        
        def count_primes_up_to_n(n):
            count = 0
            for i in range(2, n + 1):
                if all(i % j != 0 for j in range(2, int(i**0.5) + 1)):
                    count += 1
            return count
        
        def factorial(num):
            if num == 0:
                return 1
            return num * factorial(num - 1)
        
        primes = sieve_of_eratosthenes(n)
        prime_count = len(primes)
        non_prime_count = n - prime_count
        
        prime_permutations = factorial(prime_count)
        non_prime_permutations = factorial(non_prime_count)
        
        return (prime_permutations * non_prime_permutations) % (10**9 + 7)
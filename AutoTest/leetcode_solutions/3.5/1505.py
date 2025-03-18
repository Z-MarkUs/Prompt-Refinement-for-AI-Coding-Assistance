class Solution:
    def minInteger(self, num: str, k: int) -> str:
        n = len(num)
        num = list(num)
        pos = [collections.deque() for _ in range(10)]
        for i, digit in enumerate(num):
            pos[int(digit)].append(i)
        
        res = []
        bit = FenwickTree(n)
        
        for _ in range(n):
            for d in range(10):
                if pos[d]:
                    i = pos[d][0]
                    cost = bit.query(i)
                    if i - cost <= k:
                        k -= i - cost
                        bit.update(i, 1)
                        pos[d].popleft()
                        res.append(str(d))
                        break
        
        return ''.join(res)
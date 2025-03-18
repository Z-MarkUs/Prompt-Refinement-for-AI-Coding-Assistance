class Solution:
    def decrypt(self, code: List[int], k: int) -> List[int]:
        n = len(code)
        decrypted = [0] * n
        
        if k == 0:
            return decrypted
        
        for i in range(n):
            if k > 0:
                for j in range(1, k+1):
                    decrypted[i] += code[(i+j) % n]
            else:
                for j in range(1, abs(k)+1):
                    decrypted[i] += code[(i-j) % n]
        
        return decrypted
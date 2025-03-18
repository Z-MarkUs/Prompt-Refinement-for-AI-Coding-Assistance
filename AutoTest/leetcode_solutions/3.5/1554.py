from typing import List

class Solution:
    def differByOne(self, dict: List[str]) -> bool:
        n = len(dict)
        m = len(dict[0])
        
        for i in range(m):
            seen = set()
            for j in range(n):
                word = dict[j][:i] + '*' + dict[j][i+1:]
                if word in seen:
                    return True
                seen.add(word)
        
        return False
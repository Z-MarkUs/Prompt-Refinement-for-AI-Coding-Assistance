class Solution:
    def differByOne(self, dict: List[str]) -> bool:
        patterns = set()
        
        for word in dict:
            for i in range(len(word)):
                pattern = word[:i] + '*' + word[i+1:]
                if pattern in patterns:
                    return True
                patterns.add(pattern)
        
        return False
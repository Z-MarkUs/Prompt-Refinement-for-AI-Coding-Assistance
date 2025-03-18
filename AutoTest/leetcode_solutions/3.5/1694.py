class Solution:
    def reformatNumber(self, number: str) -> str:
        number = number.replace(" ", "").replace("-", "")
        n = len(number)
        result = []
        i = 0
        
        while i < n:
            if n - i > 4:
                result.append(number[i:i+3])
                i += 3
            elif n - i == 4:
                result.append(number[i:i+2])
                result.append(number[i+2:i+4])
                i += 4
            else:
                result.append(number[i:i+2])
                i += 2
        
        return "-".join(result)
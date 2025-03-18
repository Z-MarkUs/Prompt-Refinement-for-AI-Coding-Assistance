class Solution:
    def thousandSeparator(self, n: int) -> str:
        num_str = str(n)
        if len(num_str) <= 3:
            return num_str
        
        num_str = num_str[::-1]
        formatted_num = ""
        
        for i in range(len(num_str)):
            if i > 0 and i % 3 == 0:
                formatted_num += "."
            formatted_num += num_str[i]
        
        return formatted_num[::-1]

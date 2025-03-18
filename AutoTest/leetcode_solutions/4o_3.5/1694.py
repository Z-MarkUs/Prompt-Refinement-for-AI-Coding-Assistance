class Solution:
    def reformatNumber(self, number: str) -> str:
        cleaned_number = ''.join(filter(str.isdigit, number))
        groups = []
        i = 0
        
        while i < len(cleaned_number):
            if len(cleaned_number) - i == 4:
                groups.extend([cleaned_number[i:i+2], cleaned_number[i+2:i+4]])
                break
            elif len(cleaned_number) - i == 2:
                groups.append(cleaned_number[i:i+2])
                break
            elif len(cleaned_number) - i == 3:
                groups.append(cleaned_number[i:i+3])
                break
            else:
                groups.append(cleaned_number[i:i+3])
                i += 3
        
        return '-'.join(groups)
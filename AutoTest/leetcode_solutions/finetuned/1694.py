class Solution:
    def reformatNumber(self, number: str) -> str:
        clean_number = ''.join(char for char in number if char.isdigit())
        blocks = []
        i = 0
        while i < len(clean_number):
            if len(clean_number) - i > 4:
                blocks.append(clean_number[i:i+3])
                i += 3
            else:
                if len(clean_number) - i == 4:
                    blocks.extend([clean_number[i:i+2], clean_number[i+2:i+4]])
                else:
                    blocks.append(clean_number[i:])
                break
        return '-'.join(blocks)
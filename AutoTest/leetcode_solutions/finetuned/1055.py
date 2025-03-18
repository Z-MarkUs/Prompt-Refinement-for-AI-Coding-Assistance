class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        count = 0
        t_index = 0
        
        while t_index < len(target):
            count += 1
            s_index = 0
            curr_t_index = t_index
            
            while s_index < len(source) and t_index < len(target):
                if source[s_index] == target[t_index]:
                    t_index += 1
                s_index += 1
            
            if curr_t_index == t_index:
                return -1
        
        return count
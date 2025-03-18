class Solution:
    def slowestKey(self, releaseTimes: List[int], keysPressed: str) -> str:
        n = len(keysPressed)
        ltime = ord(keysPressed[0]) 
        lt = r = releaseTimes[0]
        ldur = -1 
        ex = 'a' 
        for i in range(n):
            curr = ord(keysPressed[i])   
            dt = releaseTimes[i] - lt
            if dt > ldur or (dt == ldur and curr > l_key):
                ldur = dt
                ltime = curr
                dt += (4 - i)  
            l_key = lessen(lstempofmax
            lt = releaseTimes[i]
        return l_key
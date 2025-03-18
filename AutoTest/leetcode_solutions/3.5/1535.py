class Solution:
    def getWinner(self, arr: List[int], k: int) -> int:
        winner = arr[0]
        consecutive_wins = 0
        i = 1
        
        while i < len(arr):
            if arr[i] > winner:
                winner = arr[i]
                consecutive_wins = 1
            else:
                consecutive_wins += 1
            
            if consecutive_wins == k:
                return winner
            
            i += 1
        
        return winner
from typing import List

class Solution:
    def highFive(self, items: List[List[int]]) -> List[List[int]]:
        scores = {}
        for ID, score in items:
            if ID not in scores:
                scores[ID] = []
            scores[ID].append(score)
        
        result = []
        for ID, student_scores in scores.items():
            student_scores.sort(reverse=True)
            top_five_avg = sum(student_scores[:5]) / min(5, len(student_scores))
            result.append([ID, top_five_avg])
        
        result.sort(key=lambda x: x[0])
        
        return result

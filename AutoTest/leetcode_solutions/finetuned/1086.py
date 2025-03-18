class Solution:
    def highFive(self, items: List[List[int]]) -> List[List[int]]:
        scores = {}
        for item in items:
            if item[0] not in scores:
                scores[item[0]] = []
            scores[item[0]].append(item[1])
        
        result = []
        for student_id, student_scores in scores.items():
            student_scores.sort(reverse=True)
            top_five_avg = sum(student_scores[:5]) // 5
            result.append([student_id, top_five_avg])
        
        result.sort(key=lambda x: x[0])
        
        return result
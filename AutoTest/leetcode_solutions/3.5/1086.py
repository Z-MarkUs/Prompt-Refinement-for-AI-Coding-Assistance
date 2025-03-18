```python
from collections import defaultdict

class Solution:
    def highFive(self, items: List[List[int]]) -> List[List[int]:
        scores = defaultdict(list)
        
        for ID, score in items:
            scores[ID].append(score)
        
        result = []
        for ID, score_list in scores.items():
            top_five = sorted(score_list, reverse=True)[:5]
            top_five_avg = sum(top_five) // 5
            result.append([ID, top_five_avg])
        
        result.sort(key=lambda x: x[0])
        
        return result
```
class Solution:
    def countStudents(self, students: List[int], sandwiches: List[int]) -> int:
        circular_count = students.count(0)
        square_count = students.count(1)
        
        for sandwich in sandwiches:
            if sandwich == 0:
                if circular_count > 0:
                    circular_count -= 1
                else:
                    return square_count
            else:
                if square_count > 0:
                    square_count -= 1
                else:
                    return circular_count
        
        return 0
class Solution:
    def getDecimalValue(self, head: Optional[ListNode]) -> int:
        decimal_value = 0
        current = head
        
        while current:
            decimal_value = decimal_value * 2 + current.val
            current = current.next
        
        return decimal_value
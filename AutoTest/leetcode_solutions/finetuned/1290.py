class Solution:
    def getDecimalValue(self, head: Optional[ListNode]) -> int:
        decimalValue = 0
        current = head
        while current:
            decimalValue = (decimalValue << 1) | current.val
            current = current.next
        return decimalValue
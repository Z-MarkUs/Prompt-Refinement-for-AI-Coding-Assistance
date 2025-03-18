class Solution:
    def dayOfYear(self, date: str) -> int:
        year, month, day = map(int, date.split('-'))
        days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        leap_days_in_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        leap_year = (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)
        days = sum(leap_days_in_month[:month]) if leap_year else sum(days_in_month[:month])
        return days + day
#日付・計算・整形などの共通関数
import calendar 
from datetime import date, datetime 

def get_ymd_from_request(request, today=None):
    today  = today or date.today() # today未指定なら“今日”
    y =int(request.GET.get("y",today.year)) # ?y=があれば年、それ以外は今年
    m = int(request.GET.get("m",today.month)) # ?m=があれば月、それ以外は今月
    d_str = request.GET.get("d") # ?d=日付文字列
    selected = None
    if d_str:
        try:
            selected = datetime.strptime(d_str, "%Y-%m-%d").date() # 正しい形式なら日付化
        except ValueError:
            selected = None  
    return y, m, selected  

def month_matrix(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6) # 日曜(6)始まりのカレンダーにする
    weeks = cal.monthdayscalendar(year, month) 
    return weeks

def prev_next_year_month(year: int, month: int):
    prev_y, prev_m = (year -1, 12) if month == 1 else(year, month -1)  # 前月の年・月
    next_y, next_m = (year +1, 1) if month == 12 else(year, month +1)  # 次月の年・月
    return (prev_y, prev_m), (next_y, next_m) # 前月/次月のタプルを返す


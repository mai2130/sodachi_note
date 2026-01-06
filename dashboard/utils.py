# 日付・計算・整形などの共通関数
import calendar 
from datetime import date, datetime

def get_ymd_from_request(request, today=None):
    today  = today or date.today() 
    
    try:
        y = int(request.GET.get("y", today.year))
    except ValueError:
        y = today.year
        
    try:
        m = int(request.GET.get("m", today.month))
    except ValueError:
        m = today.month
        
    d_str = request.GET.get("d") 
    selected = None
    if d_str:
        try:
            selected = datetime.strptime(d_str, "%Y-%m-%d").date() 
        except ValueError:
            selected = None
            
    return y, m, selected 

def build_attendance_map(month_att_qs):
    mp = {}
    for a in month_att_qs:
        mp[a.date] =  a.status
    return mp

def build_weeks_cells(year, month, selected, attendance_map):
    cal = calendar.Calendar(firstweekday=6) # 日曜始まり
    weeks = cal.monthdatescalendar(year, month)
    
    weeks_cells = []
    for week in weeks:
        row = []
        for dt in week:
            row.append({
                "date": dt,
                "in_month":(dt.month == month),
                "selected":(selected == dt) if selected else False,
                "status": attendance_map.get(dt), 
            })
        weeks_cells.append(row)
            
            # 前月・次月
    if month == 1:
        prev_ym = (year -1, 12)
    else:
        prev_ym = (year, month -1)
                
    if month == 12:
        next_ym = (year +1, 1)
    else:
        next_ym = (year, month +1)
        
    return weeks_cells, prev_ym, next_ym
    

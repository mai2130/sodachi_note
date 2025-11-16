from datetime import date
import calendar
from django.contrib.auth.mixins import LoginRequiredMixin # ログイン必須
from django.views.generic import TemplateView
from .utils import (
    get_ymd_from_request, month_matrix, prev_next_year_month
) # utilsから関数をimport（循環回避）

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs) # 親のコンテキストを取得
        today = date.today()
        year, month, selected = get_ymd_from_request(self.request, today=today) #URL(?y,?m,?d)から年/月/選択日を取得
        weeks = month_matrix(year, month) # 月の週リストを作る
        (py, pm),(ny, nm) = prev_next_year_month(year, month) #前月・次月を求める
        
        #ダミー出欠データ
        attendance ={
            date(year, month, 1): 'present',
            date(year, month, 7): 'late_early',
            date(year, month, 10):'absent',
        }
        
        current_status = attendance.get(selected or today)
        
        last_day_prev = calendar.monthrange(py, pm)[1] #前月の最終日
                
        weeks_cells = [] 
        for w_idx,  week in enumerate(weeks):
            row = []
            
            lead_zeros = sum(1 for d in week if d == 0) if w_idx == 0 else 0
            next_counter = 1
            
            for d_idx, d in enumerate(week):    
                if d == 0:
                    if w_idx == 0:
                        day_num = last_day_prev - (lead_zeros - 1 - d_idx)
                        cell_date = date(py, pm, day_num)
                        in_month = False
                    elif w_idx == len(weeks) - 1:
                        day_num = next_counter
                        next_counter += 1
                        cell_date = date(ny, nm, day_num)
                        in_month = False
                    else:
                        day_num = next_counter
                        next_counter += 1
                        cell_date = date(ny, nm, day_num)
                        in_month =False                                        
                else:
                    cell_date = date(year, month, d)
                    in_month = True
                    
                is_selected = (selected == cell_date) if selected else False
                status = attendance.get(cell_date)
                    
                row.append({
                    "date": cell_date,
                    "in_month": in_month,
                    "selected": is_selected,
                    "status": status,
                    })
            weeks_cells.append(row)
                    
        ctx.update({ #それをテンプレートに渡す
            "weeks": weeks_cells,
            "today": today,
            "year": year,
            "month": month,
            "selected": selected,
            "prev_y": py, "prev_m": pm,
            "next_y": ny, "next_m": nm, 
            "weekdays":["日","月","火","水","木","金","土"],
        })
        
        # ここは「ダミーデータ」。後で Attendance / school_growth_logs / home_growth_logs に置換
        ctx["daily_info"] = {
            "date": selected or today,
            "attendance" : current_status or "present",
            "school_note" : "園での記録は未入力です",
            "home_note" : "家庭での記録は未入力です",          
        }      
       
        return ctx

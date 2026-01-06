from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin # ログイン必須
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from children.models import Child
from attendances.models import Attendance
from .utils import get_ymd_from_request, build_attendance_map, build_weeks_cells
# utilsから関数をimport（循環回避）

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"
    
    # テンプレに渡すデータを作成する（ctx=context）
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        user = self.request.user
        
        today = date.today()
        #URL(?y,?m,?d)から年/月/選択日を取得
        year, month, selected = get_ymd_from_request(self.request, today=today) 
        target_day = selected or today
        
        child = None
        attendance_map = {}
        day_attendance = None
        
        #  園（施設）
        if user.is_facility():
            ctx["mode"] = "nursery"

            # 施設は「確認したい園児」をGET(child_id)で受け取る設計
            child_id = self.request.GET.get("child_id")
            if child_id:
                # Nurseryは user.nursery がある想定（あなたの既存設計）
                child = get_object_or_404(
                    Child.objects.filter(nursery=user.nursery),
                    id=child_id
                )

            ctx["child"] = child

            if child:
                month_att = Attendance.objects.filter(
                    child=child,
                    date__year=year,
                    date__month=month,
                )
                attendance_map = build_attendance_map(month_att)

                att = Attendance.objects.filter(child=child, date=target_day).first()
                day_attendance = att.status if att else None

        #  保護者
        elif user.is_guardian():
            ctx["mode"] = "guardian"

            # A案：active_child を使う（子ども選択UIなし）
            child = user.active_child
            if not child:
                first_link = user.family_links.select_related("child").first()
                if first_link:
                    child = first_link.child
                    user.active_child = child
                    user.save(update_fields=["active_child"])            
            
            ctx["child"] = child

            if child:
                month_att = Attendance.objects.filter(
                    child=child,
                    date__year=year,
                    date__month=month,
                )
                attendance_map = build_attendance_map(month_att)

                att = Attendance.objects.filter(child=child, date=target_day).first()
                day_attendance = att.status if att else None
            else:
                messages.error(self.request, "園児が選択されていません（認証コードで登録してください）")

        # 共通：カレンダー
        weeks_cells, prev_ym, next_ym = build_weeks_cells(
            year=year,
            month=month,
            selected=selected,
            attendance_map=attendance_map,
        )
        prev_y, prev_m = prev_ym
        next_y, next_m = next_ym

        ctx.update({
            "today": today,
            "year": year,
            "month": month,
            "selected": selected,
            "weeks": weeks_cells,
            "prev_y": prev_y,
            "prev_m": prev_m,
            "next_y": next_y,
            "next_m": next_m,
            "weekdays": ["日", "月", "火", "水", "木", "金", "土"],
        })

        # テンプレ用：daily_info に統一（重要）
        ctx["daily_info"] = {
            "date": target_day,
            "attendance": day_attendance,  # 0/1/2/None
        }

        return ctx

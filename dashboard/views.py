from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from children.models import Child
from attendances.models import Attendance
from .utils import get_ymd_from_request, build_attendance_map, build_weeks_cells


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        request = self.request
        user = request.user

        today = date.today()
        year, month, selected = get_ymd_from_request(request, today=today)
        target_day = selected or today

        child = None
        month_att = None
        attendance_map = {}
        day_attendance = None

        ctx["nursery_missing"] = False
        ctx["child_missing"] = False

        # 園（施設）
        if user.is_facility():
            ctx["mode"] = "nursery"

            nursery = getattr(user, "nursery", None)

            if nursery is not None:
                nursery_children = Child.objects.filter(nursery=nursery).order_by("id")
                ctx["nursery_children"] = nursery_children

                child_id = request.GET.get("child_id", "")
                ctx["child_id"] = child_id

                # 1. GETのchild_idがあれば最優先
                if child_id:
                    child = get_object_or_404(
                        Child.objects.filter(nursery=nursery),
                        id=child_id
                    )

                # 2. child_idがなければ active_child を使う
                elif user.active_child and user.active_child.nursery_id == nursery.id:
                    child = user.active_child

                # 3. それもなければ先頭の園児
                else:
                    child = nursery_children.first()

                # child があるときだけ active_child を更新
                if child and user.active_child_id != child.id:
                    user.active_child = child
                    user.save(update_fields=["active_child"])

                # 園児が1人もいない場合
                if child is None:
                    ctx["child_missing"] = True

            else:
                ctx["nursery_children"] = Child.objects.none()
                ctx["child_id"] = ""
                ctx["nursery_missing"] = True

                if user.active_child_id is not None:
                    user.active_child = None
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

        # 保護者
        elif user.is_guardian():
            ctx["mode"] = "guardian"

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
                messages.error(request, "園児が選択されていません（認証コードで登録してください）")

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

        ctx["daily_info"] = {
            "date": target_day,
            "attendance": day_attendance,
        }

        return ctx
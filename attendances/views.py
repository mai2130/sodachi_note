from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import Attendance


@login_required
@require_POST
def guardian_attendance_upsert(request):
    print("=== upsert start ===")
    print("POST:", dict(request.POST))
    print("GET:", dict(request.GET))
    print("user:", request.user, "active_child_id:", request.user.active_child_id)
    
    ymd = request.POST.get("date")
    status = request.POST.get("status")
    print("ymd:", ymd, "status:", status)

    child = getattr(request.user,"active_child",None)
    if not child:
        print("STOP: child is None")
        messages.error(request, "園児が選択されていません")
        return redirect(_build_home_url(request))

    # 日付チェック
    try:
        date_obj = datetime.strptime(ymd, "%Y-%m-%d").date()
    except (TypeError, ValueError)as e:
        print("STOP: bad date", e)
        messages.error(request, "日付を確認してください")
        return redirect(_build_home_url(request))

    # 出欠チェック
    try:
        status_int = int(status)
    except(TypeError, ValueError)as e:
        print("STOP: bad status", e)
        messages.error(request,"出欠情報を確認してください")
        return redirect(_build_home_url(request))
    
    valid = {c[0] for c in Attendance.Status.choices}
    if status_int not in valid:
        print("STOP: invalid status", status_int, valid)
        messages.error(request, "出欠情報を確認してください")
        return redirect(_build_home_url(request))
    
    obj, created = Attendance.objects.update_or_create(
        child=child,
        date=date_obj,
        defaults={"status": status_int},
    )
    print("SAVED:", obj.id, created)

    return redirect(_build_home_url(request))

def _build_home_url(request):
    base = reverse("dashboard:home")

    y = request.GET.get("y")
    m = request.GET.get("m")
    d = request.GET.get("d")

    query = []
    if y: query.append(f"y={y}")
    if m: query.append(f"m={m}")
    if d: query.append(f"d={d}")

    return f"{base}?{'&'.join(query)}" if query else base

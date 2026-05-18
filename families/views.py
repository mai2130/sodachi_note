from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Family

@login_required
def family_info(request):
    child = getattr(request.user, "active_child", None)
    if child is None:
        return redirect("dashboard:home")
    
    get_object_or_404(Family, child=child, guardian=request.user)

    links = (
        Family.objects
        .filter(child=child)
        .select_related("guardian")
        .order_by("relationship", "id")
    )

    slots = []
    seen_guardian_ids = set()

    for f in links:
        if f.guardian_id in seen_guardian_ids:
            continue

        seen_guardian_ids.add(f.guardian_id)

        slots.append({
            "pk": f.pk,
            "label": f.get_relationship_display(),
            "name": f"{f.guardian.last_name} {f.guardian.first_name}".strip() or f.guardian.username,
            "email": f.guardian.email,
        })

        if len(slots) >= 5:
            break
    while len(slots) < 5:
        slots.append({
            "pk": None,
            "label": "",
            "name": "",
            "email": "",
        })
    
    return render(
        request,
        "families/family_info.html",
        {"child": child, "slots": slots},
    )

@login_required
def family_confirm(request, pk):
    child = getattr(request.user, "active_child", None)
    if child is None:
        return redirect("families:info")

    # 覗き見防止
    get_object_or_404(Family, child=child, guardian=request.user)

    link = get_object_or_404(Family, pk=pk, child=child)
    guardian = link.guardian

    return render(request, "families/family_confirm.html", {"child": child, "link": link, "guardian": guardian})

@login_required
@require_POST
def family_delete(request, pk):
    child = getattr(request.user, "active_child", None)
    if child is None:
        return redirect("families:info")

    # 自分がこの園児の家族であることを確認
    my_link = get_object_or_404(
        Family,
        child=child,
        guardian=request.user
    )

    # 削除対象の家族リンクを取得
    link = get_object_or_404(
        Family,
        pk=pk,
        child=child
    )

    # 自分自身の家族リンクは削除できないようにする
    if link.pk == my_link.pk:
        return redirect("families:info")

    link.delete()
    return redirect("families:info")
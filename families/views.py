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

    for f in links[:5]:
        slots.append({
            "pk": f.pk,
            "label": f.get_relationship_display(),
            "name": f.guardian.get_full_name() or f.guardian.username,
            "email": f.guardian.email,
        })

    while len(slots) < 5:
        slots.append({"pk": None, "label": "", "name": "", "email": ""})

    return render(
        request,
        "families/family_info.html",
        {"child": child, "slots": slots},
    )

@login_required
def family_confirm(request, pk):
    child = getattr(request.user, "active_child", None)
    if child is None:
        return redirect("families:family_info")

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
        return redirect("families:family_info")

    # 覗き見防止
    get_object_or_404(Family, child=child, guardian=request.user)

    link = get_object_or_404(Family, pk=pk, child=child)
    link.delete()
    return redirect("families:family_info")
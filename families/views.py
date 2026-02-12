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

    buckets = {key: [] for key, _ in Family.Relationship.choices}
    for f in links:
        buckets[f.relationship].append(f)

    slots = []

    def put(relationship_value, label, max_count):
        items = buckets.get(relationship_value, [])
        for obj in items[:max_count]:
            if len(slots) >= 5:
                return
            slots.append({"pk": obj.pk, "label": label, "name": obj.guardian.username, })
    
    put(Family.Relationship.FATHER, "パパ", 1)
    put(Family.Relationship.MOTHER, "ママ", 1)
    put(Family.Relationship.GRANDFATHER, "おじいちゃん", 2)
    put(Family.Relationship.GRANDMOTHER, "おばあちゃん", 2)

    while len(slots) < 5:
        slots.append({"pk": None, "label": "", "name": ""})

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
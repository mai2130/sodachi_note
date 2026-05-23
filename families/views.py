from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Family


@login_required
def family_info(request):
    child = getattr(request.user, "active_child", None)

    if child is None:
        messages.error(request, "園児が選択されていません")
        return redirect("dashboard:home")

    # 自分のFamilyがない場合は作成する
    my_link = Family.objects.filter(
        child=child,
        guardian=request.user
    ).first()

    if my_link is None:
        my_link = Family.objects.create(
            child=child,
            guardian=request.user,
            relationship=request.user.relationship,
        )

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

        relationship_label = f.get_relationship_display()

        name = f"{f.guardian.last_name} {f.guardian.first_name}".strip()
        if not name:
            name = f.guardian.email

        slots.append({
            "pk": f.pk,
            "label": relationship_label,
            "name": name,
        })

        if len(slots) >= 5:
            break

    while len(slots) < 5:
        slots.append({
            "pk": None,
            "label": "",
            "name": "",
        })

    return render(
        request,
        "families/family_info.html",
        {
            "child": child,
            "slots": slots,
        },
    )


@login_required
def family_confirm(request, pk):
    child = getattr(request.user, "active_child", None)

    if child is None:
        messages.error(request, "園児が選択されていません")
        return redirect("dashboard:home")

    # 自分のFamilyがない場合は作成する
    my_link = Family.objects.filter(
        child=child,
        guardian=request.user
    ).first()

    if my_link is None:
        my_link = Family.objects.create(
            child=child,
            guardian=request.user,
            relationship=request.user.relationship,
        )

    link = get_object_or_404(Family, pk=pk, child=child)
    guardian = link.guardian

    return render(
        request,
        "families/family_confirm.html",
        {
            "child": child,
            "link": link,
            "guardian": guardian,
        },
    )


@login_required
@require_POST
def family_delete(request, pk):
    child = getattr(request.user, "active_child", None)

    if child is None:
        messages.error(request, "園児が選択されていません")
        return redirect("dashboard:home")

    my_link = Family.objects.filter(
        child=child,
        guardian=request.user
    ).first()

    if my_link is None:
        my_link = Family.objects.create(
            child=child,
            guardian=request.user,
            relationship=request.user.relationship,
        )

    link = get_object_or_404(
        Family,
        pk=pk,
        child=child
    )

    # 自分自身は削除できない
    if link.pk == my_link.pk:
        messages.error(request, "自分自身の家族情報を削除することはできません")
        return redirect("families:info")

    link.delete()
    messages.success(request, "家族情報を削除しました")
    return redirect("families:info")
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from invites.models import InviteCode
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import AccountManageForm


# 一覧表示
class AccountListView(LoginRequiredMixin, ListView):
    model = InviteCode
    template_name = 'invites/account_list.html'
    context_object_name = 'codes'
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        # 保護者はこの画面に入れない
        if hasattr(request.user, "is_guardian") and request.user.is_guardian():
            messages.error(request, "このページは園アカウント専用です")
            return redirect("dashboard:home")

        # 園情報がない場合もホームへ戻す
        nursery = getattr(request.user, "nursery", None)
        if nursery is None:
            messages.error(request, "この施設アカウントには園情報が登録されていません")
            return redirect("dashboard:home")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # ログインユーザーの園だけ
        nursery = getattr(self.request.user, "nursery", None)
        if nursery is None:
            return InviteCode.objects.none()

        qs = (
            InviteCode.objects
            .filter(child__nursery=nursery)
            .select_related('child', 'child__classroom')
            .order_by('-created_at')
        )
        return qs


# アカウント管理（編集・削除・認証コード発行）
class AccountManageView(LoginRequiredMixin, View):
    template_name = "invites/account_manage.html"

    def dispatch(self, request, *args, **kwargs):
        # 保護者はこの画面に入れない
        if hasattr(request.user, "is_guardian") and request.user.is_guardian():
            messages.error(request, "このページは園アカウント専用です")
            return redirect("dashboard:home")

        # 園情報がない場合はホームへ戻す
        nursery = getattr(request.user, "nursery", None)
        if nursery is None:
            messages.error(request, "この施設アカウントには園情報が登録されていません")
            return redirect("dashboard:home")

        return super().dispatch(request, *args, **kwargs)

    def get_invite(self, request, pk):
        nursery = getattr(request.user, "nursery", None)
        return get_object_or_404(
            InviteCode,
            pk=pk,
            child__nursery=nursery
        )

    def get(self, request, pk):
        invite = self.get_invite(request, pk)
        form = AccountManageForm(instance=invite.child)
        return render(request, self.template_name, {"invite": invite, "form": form})

    def post(self, request, pk):
        invite = self.get_invite(request, pk)
        form = AccountManageForm(request.POST, instance=invite.child)

        # 削除（はい）
        if "delete_yes" in request.POST:
            invite.child.delete()
            messages.success(request, "削除しました", extra_tags="account_manage_message")
            return redirect("invites:account_list")

        # 認証コード発行
        if "issue_code" in request.POST:
            if not form.is_valid():
                # 未入力なら上部エラー表示
                return render(request, self.template_name, {"invite": invite, "form": form})

            form.save()
            invite.short_code = None
            invite.users_count = 0
            invite.save()
            messages.success(request, "認証コードを発行しました！", extra_tags="account_manage_message")
            return redirect("invites:account_manage", pk=invite.pk)

        # 保存
        if form.is_valid():
            form.save()
            messages.success(request, "保存しました！", extra_tags="account_manage_message")
            return redirect("invites:account_manage", pk=invite.pk)

        return render(request, self.template_name, {"invite": invite, "form": form})


# 新規作成
class AccountCreateView(LoginRequiredMixin, View):
    template_name = "invites/account_manage.html"

    def dispatch(self, request, *args, **kwargs):
        # 保護者はこの画面に入れない
        if hasattr(request.user, "is_guardian") and request.user.is_guardian():
            messages.error(request, "このページは園アカウント専用です")
            return redirect("dashboard:home")

        # 園情報がない場合はホームへ戻す
        nursery = getattr(request.user, "nursery", None)
        if nursery is None:
            messages.error(request, "この施設アカウントには園情報が登録されていません")
            return redirect("dashboard:home")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = AccountManageForm()
        return render(request, self.template_name, {"form": form, "invite": None})

    def post(self, request):
        form = AccountManageForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "invite": None})

        nursery = getattr(request.user, "nursery", None)
        if nursery is None:
            messages.error(request, "この施設アカウントには園情報が登録されていません")
            return redirect("dashboard:home")

        child = form.save(commit=False)
        child.nursery = nursery
        child.save()
        form.save_m2m()

        invite = InviteCode.objects.create(child=child)

        return redirect("invites:account_manage", pk=invite.pk)
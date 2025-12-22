from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView  
from invites.models import InviteCode
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import AccountManageForm
import uuid
import datetime

class AccountListView(LoginRequiredMixin, ListView):
    model = InviteCode
    template_name = 'invites/account_list.html'
    context_object_name = 'codes'
    paginate_by = 5
    
    def get_queryset(self):
        # ログインユーザーの園だけ
        qs = (
            InviteCode.objects
            .filter(child__nursery=self.request.user.nursery)
            .select_related('child', 'child__classroom')
            .order_by('-created_at')
        )
        return qs

class AccountManageView(LoginRequiredMixin, View):
    template_name = "invites/account_manage.html"

    def get_invite(self, request, pk):
        # 自園の園児に紐づくInviteCodeだけ触れるように制限
        return get_object_or_404(
            InviteCode,
            pk=pk,
            child__nursery=request.user.nursery
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
            messages.success(request, "削除しました。")
            return redirect("invites:account_list")
               
        # 認証コード発行
        if "issue_code" in request.POST:
            if not form.is_valid():
                # 未入力なら上部エラー表示
                return render(request, self.template_name, {"invite": invite, "form": form})
            
            form.save()
            invite.code = str(uuid.uuid4())
            invite.save()
            messages.success(request, "認証コードを発行しました！")
            return redirect("invites:account_manage", pk=invite.pk)
        
        if form.is_valid():
            form.save()
            messages.success(request, "保存しました！")
            return redirect("invites:account_manage", pk=invite.pk)

        return render(request, self.template_name, {"invite": invite, "form": form})



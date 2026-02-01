from datetime import date
from django.views.generic import ListView , CreateView  #ListView：一覧表示用の汎用ビュー
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Board, BoardPost
from .forms import BoardForm

# 園ログイン（request.user.nursery)、保護者ログイン（request.user.active_child.nursery）のどちらでも園を取る
# 取れない場合はNone
def get_current_nursery(request):
    user = request.user

    # 園ユーザー：Nurseryが紐づいている（related_name="nursery"）
    if getattr(user, "is_facility", None) and user.is_facility():
        return getattr(user, "nursery", None)

    # 保護者ユーザー：active_child から園を辿る
    if getattr(user, "is_guardian", None) and user.is_guardian():
        child = getattr(user, "active_child", None)
        return getattr(child, "nursery", None) if child else None

    # role未設定などの保険
    return getattr(user, "nursery", None)
class BoardListView(LoginRequiredMixin, ListView):
    model = Board
    template_name = 'boards/list.html'
    context_object_name = 'boards'
    paginate_by = 5

    def get_queryset(self):
        nursery = get_current_nursery(self.request)
        if nursery is None:
            return Board.objects.none()
        
        qs =Board.objects.filter(nursery=nursery)
        
        keyword = self.request.GET.get('keyword','').strip()
        if keyword:
            qs = qs.filter(title__icontains=keyword) #icontains：大文字・小文字を区別せずに部分一致検索

        category = self.request.GET.get('category','').strip()
        if category != "":
            qs = qs.filter(category=category)

        return qs.order_by('-date', '-created_at')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["keyword"] = self.request.GET.get("keyword", "")
        ctx["category"] = self.request.GET.get("category", "")
        return ctx
    
class BoardCreateView(LoginRequiredMixin, CreateView):
    model = Board
    form_class = BoardForm
    template_name = "boards/create.html"
    success_url = reverse_lazy("boards:list")
    
    @transaction.atomic
    def form_valid(self, form):
        nursery = get_current_nursery(self.request)
        if nursery is None:
            return redirect("boards:list")
        
        board = form.save(commit = False)
        board.nursery = nursery
        board.user = self.request.user
        board.save()
        # dateが空なら今日
        if not board.date:
            board.date = date.today()

        board.save()
        
        comment =self.request.POST.get("comment","").strip()
        if comment:
            BoardPost.objects.create(
                board = board,
                user =self.request.user,
                comment =comment,
            )
            
        return redirect(self.success_url)
    
@login_required
def board_detail(request, pk):
    nursery = get_current_nursery(request)
    if nursery is None:
        return redirect("boards:list")

    # ① ログイン中の園の投稿だけ取得（他園の投稿は404）
    board = get_object_or_404(
        Board,
        pk=pk,
        nursery=nursery
    )
    
    error_message = ""
    # ② POST（削除 or コメント投稿）
    if request.method == "POST":
        # a) 削除ボタンが押された場合
        if "delete" in request.POST:
            if request.user == board.user:
                board.delete()
                return redirect("boards:list")
            else:
                error_message = "削除できるのは投稿者のみです。"
        # b) コメント投稿のとき
        else:
            comment = request.POST.get("comment", "").strip()
            # 入力されていればコメントを保存
            if comment:
                BoardPost.objects.create(
                    board=board,
                    user=request.user,
                    comment=comment,
                )
                return redirect('boards:detail', pk=board.pk)
            else:
                # 何も入力されていなければエラーメッセージ
                error_message = "コメントを入力してください。"

    #回答一覧（古い順）をページング           
    posts_qs = board.posts.order_by('created_at')
    paginator = Paginator(posts_qs, 5) #1ページあたり5件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "board": board,
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "error_message": error_message,
    }
    return render(request, "boards/detail.html", context)
    
        


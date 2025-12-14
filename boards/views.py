from django.views.generic import ListView , CreateView  #ListView：一覧表示用の汎用ビュー
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Board, BoardPost
from .forms import BoardForm


class BoardListView(ListView):
    model = Board
    template_name = 'boards/list.html'
    context_object_name = 'boards'
    paginate_by = 5

    def get_queryset(self):
        qs =Board.objects.filter(nursery=self.request.user.nursery)
        
        keyword = self.request.GET.get('keyword')
        if keyword:
            qs = qs.filter(title__icontains=keyword) #icontains：大文字・小文字を区別せずに部分一致検索

        category = self.request.GET.get('category')
        if category :
            qs = qs.filter(category=category)

        return qs.order_by('-date')
    
class BoardCreateView(LoginRequiredMixin, CreateView):
    model = Board
    form_class = BoardForm
    template_name = "boards/create.html"
    success_url = reverse_lazy("boards:list")
    
    @transaction.atomic
    def form_valid(self, form):
        board = form.save(commit = False)
        board.nursery = self.request.user.nursery
        board.user = self.request.user
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
    # ① ログイン中の園の投稿だけ取得（他園の投稿は404）
    board = get_object_or_404(
        Board,
        pk=pk,
        nursery=request.user.nursery
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
    
        


"""
URL configuration for sodachi_note project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.urls',"accounts"), namespace="accounts")),
    path('accounts/', include('django.contrib.auth.urls')),#ログイン/ログアウト/パスワード再設定
    path("growthlogs/",include(("schoollogs.urls", "schoollogs"),namespace="schoollogs")),
    path("notices/",include(("notices.urls", "notices"), namespace="notices")),
    path("boards/",include(("boards.urls", "boards"), namespace="boards")),
    path("mypage/", include(("nurseries.urls", "nurseries"), namespace="nurseries")),
    path("invites/", include(("invites.urls", "invites"), namespace="invites")),
    path("attendances/", include(("attendances.urls", "attendances"), namespace="attendances")),
    path('home/', include(("dashboard.urls" , "dashboard"), namespace="dashboard")),
    path('', include(("portfolio.urls" ,"portfolio"), namespace="portfolio")), #トップページ
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
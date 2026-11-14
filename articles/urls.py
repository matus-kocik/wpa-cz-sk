from django.urls import path

from .views import ArticleFileView, ArticleImageView, ArticleListView

urlpatterns = [
    path("", ArticleListView.as_view(), name="article_list"),
    path("<slug:slug>/pdf/", ArticleFileView.as_view(), name="article_pdf"),
    path("<slug:slug>/obrazek/", ArticleImageView.as_view(), name="article_image"),
]

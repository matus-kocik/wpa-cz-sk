import mimetypes
from pathlib import Path

from django.db.models import Q
from django.http import FileResponse, Http404
from django.views import View
from django.views.generic import ListView, TemplateView

from .models import Article, Category


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_articles"] = (
            Article.objects.published()
            .select_related("category")
            .order_by("-publication_date", "-pk")[:4]
        )
        return context


class ArticleListView(ListView):
    template_name = "articles/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Article.objects.published()
            .select_related("category")
            .prefetch_related("contributors__member__user")
        )
        self.query = self.request.GET.get("q", "").strip()[:200]
        self.category = self.request.GET.get("category", "")[:100]
        self.year = self.request.GET.get("year", "")[:10]
        self.sort = self.request.GET.get("sort", "oldest")
        if self.sort not in ("oldest", "newest"):
            self.sort = "oldest"
        if self.query:
            # Match each search word in public metadata, never in internal notes or PDF contents.
            for word in self.query.split()[:10]:
                qs = qs.filter(
                    Q(title__icontains=word)
                    | Q(summary__icontains=word)
                    | Q(pdf_title__icontains=word)
                    | Q(published_in__icontains=word)
                    | Q(contributors__name__icontains=word)
                    | Q(contributors__member__user__first_name__icontains=word)
                    | Q(contributors__member__user__last_name__icontains=word)
                )
        if self.category:
            qs = qs.filter(category__slug=self.category)
        if self.year:
            if (
                self.year.isdecimal()
                and len(self.year) == 4
                and 1900 <= int(self.year) <= 9999
            ):
                qs = qs.filter(publication_date__year=int(self.year))
            else:
                qs = qs.none()
        order = (
            ("publication_date", "pk")
            if self.sort == "oldest"
            else ("-publication_date", "-pk")
        )
        return qs.distinct().order_by(*order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        public = Article.objects.published()
        context.update(
            query=self.query,
            selected_category=self.category,
            selected_year=self.year,
            selected_sort=self.sort,
            categories=Category.objects.filter(articles__in=public)
            .distinct()
            .order_by("order", "name"),
            years=public.dates("publication_date", "year", order="DESC"),
        )
        params = self.request.GET.copy()
        params.pop("page", None)
        context["filter_query"] = params.urlencode()
        return context


class ArticleFileView(View):
    field_name = "pdf_file"

    def get(self, request, slug):
        try:
            article = Article.objects.published().get(slug=slug)
            field = getattr(article, self.field_name)
            if not field:
                raise Http404
            filename = Path(field.name).name
            content_type = "application/pdf"
            if self.field_name == "main_image":
                content_type = mimetypes.guess_type(filename)[0]
                if content_type not in (
                    "image/jpeg",
                    "image/png",
                    "image/webp",
                    "image/gif",
                    "image/avif",
                ):
                    raise Http404
            response = FileResponse(
                field.open("rb"),
                as_attachment=False,
                filename=filename,
                content_type=content_type,
            )
            response["X-Content-Type-Options"] = "nosniff"
            return response
        except (Article.DoesNotExist, FileNotFoundError):
            raise Http404("Soubor článku není dostupný.") from None


class ArticleImageView(ArticleFileView):
    field_name = "main_image"

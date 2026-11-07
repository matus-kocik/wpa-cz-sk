from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Event


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Event.objects.filter(is_public=True)
            .exclude(slug="")
            .annotate(effective_end=Coalesce("end_date", "start_date"))
        )
        now = timezone.now()
        past = Q(dates_only=True, effective_end__date__lt=timezone.localdate(now)) | Q(
            dates_only=False, effective_end__lt=now
        )
        if self.request.GET.get("archive") == "1":
            return qs.filter(past).order_by("-start_date", "pk")
        return qs.exclude(past).order_by("start_date", "pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["archive"] = self.request.GET.get("archive") == "1"
        return context


class EventDetailView(DetailView):
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(is_public=True).exclude(slug="")

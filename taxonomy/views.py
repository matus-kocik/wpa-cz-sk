from django.shortcuts import render
from django.views.generic import DetailView

from .models import Family, Species


class SpeciesDetailView(DetailView):
    model = Species
    template_name = "taxonomy/species_detail.html"
    context_object_name = "object"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Species.objects.filter(is_active=True)


    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)

        return Species.objects.get(slug=slug, is_active=True)


def species_list_view(request):
    families = Family.objects.prefetch_related(
        "subfamilies__genera__species"
    )
    return render(
        request,
        "taxonomy/species_list.html",
        {
            "families": families,
        },
    )

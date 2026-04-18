from django.shortcuts import render
from django.views.generic import DetailView

from members.models import MemberProfile
from profiles.models import PublicProfile


class PublicProfileDetailView(DetailView):
    model = PublicProfile
    template_name = "profiles/public_profile_detail.html"
    context_object_name = "profile"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return PublicProfile.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_member"] = self.request.user.is_authenticated
        return context


def members_view(request):
    members = MemberProfile.objects.all()
    return render(
        request,
        "members.html",
        {
            "members": members,
        },
    )

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import redirect, render
from django.views.generic import DetailView, UpdateView

from members.models import MemberProfile
from profiles.forms import GalleryFormSet, PublicProfileForm, VideoFormSet
from profiles.models import PublicProfile


class PublicProfileDetailView(DetailView):
    model = PublicProfile
    template_name = "profiles/public_profile_detail.html"
    context_object_name = "profile"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        qs = PublicProfile.objects.all()

        if self.request.user.is_authenticated:
            return qs.filter(
                models.Q(is_public=True) |
                models.Q(member__user=self.request.user)
            )

        return qs.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_member"] = self.request.user.is_authenticated
        context["is_owner"] = (
            self.request.user.is_authenticated and
            self.request.user == self.object.member.user
        )

        return context


class PublicProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = PublicProfile
    template_name = "profiles/public_profile_edit.html"
    context_object_name = "profile"
    form_class = PublicProfileForm

    def get_object(self):
        return self.request.user.member_profile.public_profile

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["gallery_formset"] = GalleryFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="gallery"
            )
            context["video_formset"] = VideoFormSet(
                self.request.POST,
                instance=self.object,
                prefix="videos"
            )
        else:
            context["gallery_formset"] = GalleryFormSet(
                instance=self.object,
                prefix="gallery"
            )
            context["video_formset"] = VideoFormSet(
                instance=self.object,
                prefix="videos"
            )

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        gallery_formset = context["gallery_formset"]
        video_formset = context["video_formset"]

        # force correct instance (prevent POST tampering)
        gallery_formset.instance = self.object
        video_formset.instance = self.object

        if gallery_formset.is_valid() and video_formset.is_valid():
            # enforce limits (defense in depth)
            if gallery_formset.total_form_count() > 6:
                gallery_formset._non_form_errors = gallery_formset.error_class([
                    "Maximálně 6 obrázků."
                ])
                return self.form_invalid(form)

            if video_formset.total_form_count() > 3:
                video_formset._non_form_errors = video_formset.error_class([
                    "Maximálně 3 videa."
                ])
                return self.form_invalid(form)

            print("CLEANED AVATAR:", form.cleaned_data.get("avatar"))
            self.object = form.save()

            gallery_formset.instance = self.object
            video_formset.instance = self.object

            gallery_formset.save()
            video_formset.save()

            return redirect(self.get_success_url())

        return self.form_invalid(form)


def members_view(request):
    members = MemberProfile.objects.all()
    return render(
        request,
        "members.html",
        {
            "members": members,
        },
    )

from django.views.generic.edit import FormView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.conf import settings
from .forms import ContactForm


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]

        send_mail(
            subject=f"{subject} od {name}",
            message=message + f"\n\nKontakt: {email}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["matuskocik@gmail.com"],
        )
        return super().form_valid(form)

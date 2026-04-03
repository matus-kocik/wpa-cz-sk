from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django_countries.fields import Country
from django_ratelimit.decorators import ratelimit

from .forms import MembershipApplicationForm


@method_decorator(
    ratelimit(key="post:email", rate="2/d", method="POST", block=True),
    name="dispatch",
)
@method_decorator(
    ratelimit(key="ip", rate="5/d", method="POST", block=True),
    name="dispatch",
)
class MembershipApplicationView(FormView):
    template_name = "members/membership_application.html"
    form_class = MembershipApplicationForm
    success_url = reverse_lazy("membership_application")

    def form_valid(self, form):
        form.save()
        data = form.cleaned_data

        country_name = Country(data["country"]).name if data.get("country") else ""
        data["country_name"] = country_name

        html_content = render_to_string("members/membership_email.html", data)

        text_content = "\n".join(
            [
                f"Příjmení: {data['last_name']}",
                f"Jméno: {data['first_name']}",
                f"Titul: {data['academic_title']}",
                f"Datum narození: {data['birth_date']}",
                "",
                f"Adresa: {data['street']} {data['house_number']}, {data['postal_code']} {data['city']}",
                f"Okres: {data['district']}",
                f"Stát: {country_name}",
                "",
                f"Telefon: {data['phone_number']}",
                f"E-mail: {data['email']}",
                "",
                f"Poznámky: {data['notes']}",
                f"V: {data['declaration_place']}",
                f"Dne: {data['declaration_date']}",
                f"Podpis: {data['declaration_signature']}",
            ]
        )

        msg = EmailMultiAlternatives(
            subject="Nová přihláška do WPA CZ-SK",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.APPLICATION_RECEIVER_EMAIL],
            reply_to=[data["email"]],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        user_subject = "Potvrzení odeslání přihlášky – WPA CZ-SK"
        user_text = render_to_string("members/membership_user_email.txt", data)
        user_html = render_to_string("members/membership_user_email.html", data)

        user_msg = EmailMultiAlternatives(
            subject=user_subject,
            body=user_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[data["email"]],
        )
        user_msg.attach_alternative(user_html, "text/html")
        user_msg.send()

        messages.success(self.request, "Přihláška byla úspěšně odeslána. Děkujeme!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Formulář obsahuje chyby. Prosím opravte je a zkuste to znovu.",
        )
        return super().form_invalid(form)

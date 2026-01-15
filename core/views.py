from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django_countries.fields import Country
from django_ratelimit.decorators import ratelimit

from .forms import ContactForm, MembershipApplicationForm


@method_decorator(
    ratelimit(key="post:email", rate="3/h", method="POST", block=True),
    name="dispatch",
)
@method_decorator(
    ratelimit(key="ip", rate="10/h", method="POST", block=True),
    name="dispatch",
)
class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        data = form.cleaned_data

        html_content = render_to_string("contact_email.html", data)

        text_content = f"""
    Jméno: {data["first_name"]}
    Příjmení: {data["last_name"]}
    Email: {data["email"]}
    Předmět: {data["subject"]}

    Zpráva:
    {data["message_body"]}
    """

        msg = EmailMultiAlternatives(
            subject=f"{data['subject']} – zpráva z webu",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECEIVER_EMAIL],
            reply_to=[data["email"]],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        user_subject = "Potvrzení – zpráva z kontaktního formuláře"
        user_text = render_to_string("contact_user_email.txt", data)
        user_html = render_to_string("contact_user_email.html", data)

        user_msg = EmailMultiAlternatives(
            subject=user_subject,
            body=user_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[data["email"]],
        )
        user_msg.attach_alternative(user_html, "text/html")
        user_msg.send()

        messages.success(self.request, "Zpráva byla úspěšně odeslána. Děkujeme!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Formulář obsahuje chyby. Prosím opravte je a zkuste to znovu.",
        )
        return super().form_invalid(form)


@method_decorator(
    ratelimit(key="post:email", rate="2/d", method="POST", block=True),
    name="dispatch",
)
@method_decorator(
    ratelimit(key="ip", rate="5/d", method="POST", block=True),
    name="dispatch",
)
class MembershipApplicationView(FormView):
    template_name = "membership_application.html"
    form_class = MembershipApplicationForm
    success_url = reverse_lazy("membership_application")

    def form_valid(self, form):
        data = form.cleaned_data

        html_content = render_to_string("membership_email.html", data)

        text_content = "\n".join(
            [
                f"Příjmení: {data.get('last_name', '')}",
                f"Jméno: {data.get('first_name', '')}",
                f"Titul: {data.get('title', '')}",
                f"Datum narození: {data.get('birth_date', '')}",
                "",
                f"Adresa: {data.get('street', '')} {data.get('house_number', '')}, {data.get('postal_code', '')} {data.get('city', '')}",
                f"Okres: {data.get('district', '')}",
                f"Stát: {Country(data.get('country', '')).name if data.get('country') else ''}",
                "",
                f"Telefon: {data.get('phone_number', '')}",
                f"E-mail: {data.get('email', '')}",
                "",
                f"Poznámky: {data.get('notes', '')}",
                f"V: {data.get('declaration_place', '')}",
                f"Dne: {data.get('declaration_date', '')}",
                f"Podpis: {data.get('declaration_signature', '')}",
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
        user_text = render_to_string("membership_user_email.txt", data)
        user_html = render_to_string("membership_user_email.html", data)

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

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django_ratelimit.decorators import ratelimit

if settings.DEBUG:
    RATE_EMAIL = "50/h"
    RATE_IP_MIN = "50/m"
    RATE_IP_HOUR = "200/h"
else:
    RATE_EMAIL = "3/h"
    RATE_IP_MIN = "5/m"
    RATE_IP_HOUR = "10/h"

from .forms import ContactForm


@method_decorator(
    ratelimit(key="post:email", rate=RATE_EMAIL, method="POST", block=True),
    name="dispatch",
)
@method_decorator(
    ratelimit(key="ip", rate=RATE_IP_MIN, method="POST", block=True),
    name="dispatch",
)
@method_decorator(
    ratelimit(key="ip", rate=RATE_IP_HOUR, method="POST", block=True),
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

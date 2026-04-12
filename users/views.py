from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView


class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        messages.success(self.request, "Byli jste úspěšně přihlášeni.")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Byli jste úspěšně odhlášeni.")
        return super().dispatch(request, *args, **kwargs)

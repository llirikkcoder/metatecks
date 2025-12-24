from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View, FormView, CreateView

# from apps.users.email import send_registration_email
# from apps.users.email import send_registration_email, send_reset_password_email
from apps.users.favorites_utils import update_favorites_after_login
from apps.users.models import User
from apps.utils.views_mixins import JsonFormViewMixin
from .forms import LoginForm, RegistrationForm, ResetPasswordForm


class LogoutView(View):
    """
    Разлогиниваем юзера и перебрасываем на главную
    """

    def get(self, request, *args, **kwargs):
        logout(request)
        next_url = request.GET.get('next')
        redirect_to = (
            next_url
            if next_url and not next_url.startswith('/account/')
            else reverse('home')
        )
        return HttpResponseRedirect(redirect_to=redirect_to)


class LoginView(JsonFormViewMixin, FormView):
    """
    Логин
    """
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = self.POST.get('remember')
        if not remember_me:
            self.request.session.set_expiry(0)

        user = authenticate(**form.cleaned_data)
        if user:
            login(self.request, user)

        update_favorites_after_login(self.request)

        current_url = self.POST.get('current_url')
        redirect_url = current_url or reverse('home')
        # redirect_url = current_url or reverse('profile:home')

        response = {'redirect_url': redirect_url}
        return JsonResponse(response)


class RegistrationView(JsonFormViewMixin, CreateView):
    """
    Регистрация
    """
    form_class = RegistrationForm
    model = User

    def get_success_url(self):
        # чтобы Django не ругалась
        return reverse('home')

    def get_form(self, *args, **kwargs):
        form = self.form_class(self.POST)
        return form

    def form_valid(self, form):
        super().form_valid(form)
        user = form.instance

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, user)

        # send_registration_email(user)

        update_favorites_after_login(self.request)

        current_url = self.POST.get('current_url')
        redirect_url = current_url or reverse('home')
        # redirect_url = current_url or reverse('profile:home')

        data = {'result': 'ok', 'redirect_url': redirect_url}
        # data = {'redirect_url': '{}?p=first_visit'.format(redirect_url)}
        return JsonResponse(data)


class ResetPasswordView(JsonFormViewMixin, FormView):
    """
    Обновляем пароль и отправляем юзеру
    """
    form_class = ResetPasswordForm

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        user = User.objects.get(email__iexact=email)

        reset_pass(user)
        response = {'result': 'ok'}
        return JsonResponse({'response': response})


def reset_pass(user):
    # куда-то в utils
    password = User.objects.make_random_password(length=10)
    user.set_password(password)
    send_reset_password_email(user, password)
    user.save()

from allauth.account.forms import (
    LoginForm,
    SignupForm,
    ResetPasswordForm,
    ChangePasswordForm,
    SetPasswordForm,
)

def add_blue_class(field):
    existing = field.widget.attrs.get("class", "")
    field.widget.attrs["class"] = (existing + " auth-input").strip()


class BootstrapLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_blue_class(field)


class BootstrapSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_blue_class(field)


class BootstrapResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_blue_class(field)


class BootstrapChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_blue_class(field)


class BootstrapSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_blue_class(field)

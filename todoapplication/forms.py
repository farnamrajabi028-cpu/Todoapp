import re

from django import forms
from django.core.exceptions import ValidationError

from .validators import validate_iranian_mobile


class PhoneOTPRequestForm(forms.Form):
    phone_number = forms.CharField(
        label="شماره همراه",
        max_length=16,
        widget=forms.TextInput(
            attrs={
                "placeholder": "09123456789",
                "inputmode": "tel",
                "autocomplete": "tel",
                "dir": "ltr",
            }
        ),
    )

    def clean_phone_number(self):
        try:
            return validate_iranian_mobile(
                self.cleaned_data["phone_number"]
            )
        except ValidationError as error:
            raise forms.ValidationError(
                error.messages
            ) from error


class PhoneOTPVerifyForm(forms.Form):
    code = forms.CharField(
        label="کد تأیید",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "placeholder": "کد ۶ رقمی",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "dir": "ltr",
                "maxlength": "6",
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip().translate(
            str.maketrans(
                "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
                "01234567890123456789",
            )
        )

        if not re.fullmatch(r"\d{6}", code):
            raise forms.ValidationError(
                "کد تأیید باید دقیقاً ۶ رقم باشد."
            )

        return code

import re

from django.core.exceptions import ValidationError


IRAN_MOBILE_PATTERN = re.compile(r"^09\d{9}$")


def normalize_phone_number(phone_number):
    phone_number = str(phone_number or "").strip()

    translation_table = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789",
    )
    phone_number = phone_number.translate(translation_table)

    phone_number = re.sub(r"[\s\-()]", "", phone_number)

    if phone_number.startswith("+98"):
        phone_number = "0" + phone_number[3:]
    elif phone_number.startswith("0098"):
        phone_number = "0" + phone_number[4:]
    elif phone_number.startswith("98") and len(phone_number) == 12:
        phone_number = "0" + phone_number[2:]

    return phone_number


def validate_iranian_mobile(phone_number):
    normalized_phone = normalize_phone_number(phone_number)

    if not IRAN_MOBILE_PATTERN.fullmatch(normalized_phone):
        raise ValidationError(
            "شماره همراه باید یک شماره معتبر ایرانی مانند 09123456789 باشد."
        )

    return normalized_phone

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from todoapplication.models import PhoneOTP
from todoapplication.validators import validate_iranian_mobile


OTP_EXPIRATION_MINUTES = 2
OTP_MAX_ATTEMPTS = 5


class OTPError(Exception):
    pass


class OTPExpiredError(OTPError):
    pass


class OTPInvalidError(OTPError):
    pass


class OTPAttemptsExceededError(OTPError):
    pass


def generate_otp_code():
    return f"{secrets.randbelow(1_000_000):06d}"


def send_sms(phone_number, code):
    if settings.DEBUG:
        print(f"OTP for {phone_number}: {code}")
        return

    raise NotImplementedError("SMS provider is not configured.")


@transaction.atomic
def create_and_send_otp(phone_number):
    phone_number = validate_iranian_mobile(phone_number)
    now = timezone.now()

    PhoneOTP.objects.filter(
        phone_number=phone_number,
        is_used=False,
    ).update(is_used=True)

    code = generate_otp_code()

    otp = PhoneOTP.objects.create(
        phone_number=phone_number,
        code_hash=make_password(code),
        expires_at=now + timedelta(minutes=OTP_EXPIRATION_MINUTES),
    )

    send_sms(phone_number, code)
    return otp


@transaction.atomic
def verify_otp(phone_number, code):
    phone_number = validate_iranian_mobile(phone_number)
    code = str(code or "").strip()

    otp = (
        PhoneOTP.objects.select_for_update()
        .filter(
            phone_number=phone_number,
            is_used=False,
        )
        .order_by("-created_at")
        .first()
    )

    if otp is None:
        raise OTPInvalidError("کد تأیید معتبری برای این شماره وجود ندارد.")

    if otp.expires_at <= timezone.now():
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        raise OTPExpiredError("کد تأیید منقضی شده است.")

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        raise OTPAttemptsExceededError("تعداد تلاش‌های مجاز تمام شده است.")

    if not check_password(code, otp.code_hash):
        otp.attempts += 1

        if otp.attempts >= OTP_MAX_ATTEMPTS:
            otp.is_used = True

        otp.save(update_fields=["attempts", "is_used"])
        raise OTPInvalidError("کد تأیید اشتباه است.")

    otp.is_used = True
    otp.save(update_fields=["is_used"])
    return otp

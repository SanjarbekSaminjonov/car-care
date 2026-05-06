import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.cars.models import Car, MembershipRole, MembershipStatus
from apps.maintenance.models import MaintenanceRecord, MaintenanceStatus
from apps.telegram.models import TelegramAccount
from apps.webapp.auth import validate_telegram_init_data
from apps.webapp.forms import MaintenanceCreateForm
from services.maintenance_service import create_maintenance_for_chat
from services.telegram_account_service import sync_telegram_account


class WebAppLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("webapp:dashboard")

        dev_user_id = request.GET.get("dev_telegram_user_id", "").strip()
        if settings.DEBUG and dev_user_id:
            account = TelegramAccount.objects.filter(telegram_user_id=dev_user_id).first()
            if account is not None:
                login(request, account.user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect("webapp:dashboard")

        return render(request, "webapp/login.html", {"debug": settings.DEBUG})


@method_decorator(csrf_exempt, name="dispatch")
class TelegramWebAppAuthView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")

        init_data = str(payload.get("init_data") or "")
        try:
            parsed = validate_telegram_init_data(init_data)
        except ValidationError as exc:
            return JsonResponse({"success": False, "message": "; ".join(exc.messages)}, status=403)

        account = sync_telegram_account(
            chat_id=parsed.chat_id,
            telegram_user_id=parsed.user.telegram_user_id,
            username=parsed.user.username,
            first_name=parsed.user.first_name,
            last_name=parsed.user.last_name,
            language_code=parsed.user.language_code,
        )
        login(request, account.user, backend="django.contrib.auth.backends.ModelBackend")
        return JsonResponse({"success": True, "redirect_url": reverse("webapp:dashboard")})


class DashboardView(LoginRequiredMixin, View):
    login_url = "/app/login/"

    def get(self, request):
        cars = _cars_for_user(request.user).prefetch_related("maintenance_records")
        recent_records = (
            MaintenanceRecord.objects.select_related("car")
            .prefetch_related("line_items")
            .filter(
                car__memberships__user=request.user,
                car__memberships__status=MembershipStatus.ACTIVE,
                status=MaintenanceStatus.FINAL,
            )
            .annotate(media_count=Count("media_attachments", distinct=True))
            .distinct()
            .order_by("-event_date", "-created_at")[:8]
        )
        return render(
            request,
            "webapp/dashboard.html",
            {
                "cars": list(cars),
                "manageable_cars": list(_manageable_cars_for_user(request.user)),
                "recent_records": list(recent_records),
                "today": timezone.localdate(),
            },
        )


class MaintenanceCreateView(LoginRequiredMixin, View):
    login_url = "/app/login/"

    def get(self, request):
        manageable_cars = list(_manageable_cars_for_user(request.user))
        initial_car_id = request.GET.get("car") or (str(manageable_cars[0].id) if len(manageable_cars) == 1 else "")
        form = MaintenanceCreateForm(
            initial={
                "car_id": initial_car_id,
                "event_date": timezone.localdate(),
            }
        )
        return render(
            request,
            "webapp/maintenance_form.html",
            {"form": form, "manageable_cars": manageable_cars},
        )

    def post(self, request):
        manageable_cars = list(_manageable_cars_for_user(request.user))
        form = MaintenanceCreateForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "webapp/maintenance_form.html",
                {"form": form, "manageable_cars": manageable_cars},
                status=400,
            )

        car = next((item for item in manageable_cars if item.id == form.cleaned_data["car_id"]), None)
        if car is None:
            form.add_error("car_id", "Bu mashinaga servis yozuvi qo'shish huquqingiz yo'q.")
            return render(
                request,
                "webapp/maintenance_form.html",
                {"form": form, "manageable_cars": manageable_cars},
                status=403,
            )

        account = TelegramAccount.objects.filter(user=request.user, is_blocked=False).first()
        if account is None:
            return redirect("webapp:login")

        try:
            create_maintenance_for_chat(
                chat_id=account.chat_id,
                telegram_user_id=account.telegram_user_id,
                plate_number=car.plate_number,
                title=form.cleaned_data["title"],
                event_date=form.cleaned_data["event_date"],
                odometer=form.cleaned_data["odometer"],
                item_name=form.cleaned_data["item_name"],
                item_amount=form.cleaned_data["item_amount"],
            )
        except ValidationError as exc:
            form.add_error(None, "; ".join(exc.messages))
            return render(
                request,
                "webapp/maintenance_form.html",
                {"form": form, "manageable_cars": manageable_cars},
                status=400,
            )

        messages.success(request, "Servis yozuvi saqlandi.")
        return redirect("webapp:dashboard")


def _cars_for_user(user):
    return (
        Car.objects.filter(
            memberships__user=user,
            memberships__status=MembershipStatus.ACTIVE,
        )
        .distinct()
        .order_by("-created_at")
    )


def _manageable_cars_for_user(user):
    return (
        Car.objects.filter(
            memberships__user=user,
            memberships__status=MembershipStatus.ACTIVE,
            memberships__role__in=(MembershipRole.OWNER, MembershipRole.MANAGER),
        )
        .distinct()
        .order_by("-created_at")
    )

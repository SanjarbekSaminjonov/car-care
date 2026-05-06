from django import forms
from django.utils import timezone


class MaintenanceCreateForm(forms.Form):
    car_id = forms.UUIDField()
    title = forms.CharField(max_length=255)
    event_date = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    odometer = forms.IntegerField(min_value=1)
    item_name = forms.CharField(max_length=255)
    item_amount = forms.DecimalField(min_value=1, max_digits=14, decimal_places=2)

    def clean_event_date(self):
        event_date = self.cleaned_data["event_date"]
        if event_date > timezone.localdate():
            raise forms.ValidationError("Servis sanasi kelajakda bo'lishi mumkin emas.")
        return event_date

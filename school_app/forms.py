from django import forms
from .models import AttendanceRecord, InterventionCase
from django.utils import timezone

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['date', 'is_absent', 'behavioral_flag']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_absent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'behavioral_flag': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError("Cannot log attendance for a future date.")
        return date

class InterventionForm(forms.ModelForm):
    class Meta:
        model = InterventionCase
        fields = ['status', 'plan_description', 'follow_up_date', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'plan_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

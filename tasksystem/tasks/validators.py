from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_date_not_in_past(value):
    if value < timezone.now():
        raise ValidationError('due date cannot be in the past')
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import AssetTransfer


class AssetTransferForm(forms.ModelForm):
    class Meta:
        model = AssetTransfer
        fields = ["notes"]
        labels = {
            "notes": _("Notes"),
        }
        help_texts = {
            "notes": _("Any additional information regarding the transfer."),
        }

from django import forms
from .models import Order

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 20)]


class CartAddItemForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES,
                                     widget=forms.TypedChoiceField.widget(
                                         attrs={
                                             'class': 'custom-select',
                                             # 'class': 'badge badge-primary badge-pill',
                                             # 'style': 'font-size:14px;'
                                             'id': "inputGroupSelect04"
                                         }
                                     ),
                                     coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

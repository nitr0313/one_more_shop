from django import forms
from django.db.models import fields
from django.forms import ModelForm

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 101)]


class CartAddItemForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES,
                                      widget=forms.TypedChoiceField.widget(
                                          attrs={
                                              'class': 'custom-select form-control',
                                              # 'class': 'badge badge-primary badge-pill',
                                              # 'style': 'font-size:14px;'
                                              'id': "inputGroupSelect04",
                                              'size': 1,
                                              'onfocus': 'this.size=5;',
                                              'onblur': 'this.size=1;',
                                              'onchange': 'this.size=1; this.blur();',

                                          }
                                      ),
                                      coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)




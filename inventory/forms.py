from django.forms import ModelForm, Select, TextInput
from inventory.models import InventoryModel


class InventoryForm(ModelForm):
    """"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = InventoryModel
        fields = '__all__'
        exclude = []
        widgets = {
            'remark': TextInput(attrs={
                'class': 'form-control',
            }),
        }


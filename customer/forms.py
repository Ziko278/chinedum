from django.forms import ModelForm, Select, TextInput
from customer.models import CustomerModel, SaleRepModel


class CustomerForm(ModelForm):
    """"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = CustomerModel
        fields = '__all__'
        exclude = []
        widgets = {
            'description': TextInput(attrs={
                'class': 'form-control',
                'height': '300px'
            }),
        }


class SaleRepForm(ModelForm):
    """"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = SaleRepModel
        fields = '__all__'
        exclude = []
        widgets = {
            'remark': TextInput(attrs={
                'class': 'form-control',
            }),
        }


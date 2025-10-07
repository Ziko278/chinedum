from django.forms import ModelForm, Select, TextInput
from expenses.models import ExpenseModel, ExpenseTypeModel


class ExpenseTypeForm(ModelForm):
    """"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = ExpenseTypeModel
        fields = '__all__'
        exclude = []
        widgets = {
            'description': TextInput(attrs={
                'class': 'form-control',
                'height': '300px'
            }),
        }


class ExpenseForm(ModelForm):
    """"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = ExpenseModel
        fields = '__all__'
        exclude = []
        widgets = {
            'remark': TextInput(attrs={
                'class': 'form-control',
            }),
        }


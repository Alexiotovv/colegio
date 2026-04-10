from django import forms

class ExcelImportForm(forms.Form):
    archivo_excel = forms.FileField(
        label='Archivo Excel',
        help_text='Seleccione el archivo Excel con los pagos (formato .xlsx o .xls)'
    )
    anio = forms.IntegerField(
        label='Año',
        initial=2026,
        help_text='Año al que corresponden los pagos'
    )
    limpiar_antes = forms.BooleanField(
        label='Limpiar datos existentes antes de importar',
        required=False,
        initial=True,
        help_text='Si está activado, eliminará todos los pagos del año seleccionado antes de importar'
    )
from django import forms
from .models import ArchivoSituacionFinal

from django.core.exceptions import ValidationError
from colegio.Apps.SituacionFinal.models import SituacionFinal
from colegio.Apps.Alumno.models import Alumno
from colegio.Apps.Matricula.models import Matricula

class ArchivoSituacionFinalForm(forms.ModelForm):
    class Meta:
        model = ArchivoSituacionFinal
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.zip,.rar'
            })
        }


class SituacionFinalManualForm(forms.Form):
    # Tu constructor para aceptar update_mode
    def __init__(self, *args, **kwargs):
        self.update_mode = kwargs.pop('update_mode', False)
        self.matricula_id = kwargs.pop('matricula_id', None)
        super().__init__(*args, **kwargs)
    
    dni = forms.CharField(
        label='DNI del Alumno',
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese DNI (8 dígitos)',
            'id': 'dni_buscar'
        })
    )
    
    situacion_final = forms.ChoiceField(
        label='Situación Final',
        choices=[
            ('', '-- Seleccione --'),
            ('Promovido', 'Promovido'),
            ('Requiere Recuperación', 'Requiere Recuperación'),
            ('Permanece en el Grado', 'Permanece en el Grado'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'situacion_select'
        })
    )
    
    cursos = forms.CharField(
        label='Cursos con bajo rendimiento',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ej: COMUNICACIÓN - MATEMÁTICA\nDejar en blanco si es "Promovido"',
            'id': 'cursos_input'
        })
    )
    
    archivo_pdf = forms.CharField(
        label='Origen del registro',
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: PDF manual, Registro administrativo, etc.',
            'value': 'Registro manual'
        })
    )
    
    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if not dni.isdigit() or len(dni) != 8:
            raise ValidationError('El DNI debe tener 8 dígitos numéricos')
        
        # Verificar que el alumno existe
        try:
            alumno = Alumno.objects.get(DNI=dni)
        except Alumno.DoesNotExist:
            raise ValidationError(f'No existe alumno con DNI: {dni}')
        
        # Verificar que tiene matrícula activa
        matricula = Matricula.objects.filter(
            Alumno=alumno,
            AnoAcademico__activo=True
        ).first()
        
        if not matricula:
            raise ValidationError(f'El alumno {alumno.NombreCompleto()} no tiene matrícula activa en el año actual')
        
        # Guardar matrícula en cleaned_data para usar después
        self.cleaned_data['matricula_encontrada'] = matricula
        
        return dni
    
    def clean(self):
        cleaned_data = super().clean()
        dni = cleaned_data.get('dni')
        situacion = cleaned_data.get('situacion_final')
        
        if dni and situacion:
            # Obtener la matrícula que encontramos en clean_dni
            matricula = cleaned_data.get('matricula_encontrada')
            
            if matricula and not self.update_mode:  # SOLO validar duplicados si NO es modo actualización
                # VERIFICAR DUPLICADO - SituacionFinal usa unique_together en ['matricula']
                try:
                    situacion_existente = SituacionFinal.objects.get(matricula=matricula)
                    
                    # Si ya existe, mostrar error con información
                    alumno = matricula.Alumno
                    raise ValidationError({
                        'dni': f'El alumno {alumno.NombreCompleto()} ya tiene una situación final registrada para el año actual. Situación actual: {situacion_existente.situacion_final}'
                    })
                except SituacionFinal.DoesNotExist:
                    # No hay duplicado, está bien
                    pass
            elif self.update_mode and self.matricula_id:
                # En modo actualización, verificar que estamos actualizando el correcto
                try:
                    situacion_existente = SituacionFinal.objects.get(matricula_id=self.matricula_id)
                    # Si el DNI cambiado no coincide con el original
                    if situacion_existente.dni_encontrado != dni:
                        raise ValidationError({
                            'dni': f'No puede cambiar el DNI en una actualización. DNI original: {situacion_existente.dni_encontrado}'
                        })
                except SituacionFinal.DoesNotExist:
                    pass
        
        return cleaned_data
    
    def clean_cursos(self):
        situacion = self.cleaned_data.get('situacion_final')
        cursos = self.cleaned_data.get('cursos', '')
        
        if situacion in ['Requiere Recuperación', 'Permanece en el Grado'] and not cursos.strip():
            raise ValidationError(f'Debe especificar los cursos para "{situacion}"')
        
        return cursos
from django.db import models
from colegio.Apps.Matricula.models import Matricula
from colegio.Apps.AnoAcademico.models import AnoAcademico
from django.utils.translation import gettext_lazy as _

cobrar_pension = models.BooleanField(
    _("Cobrar pensión"),
    default=True,
    help_text=_("Seleccione 'Sí' para cobrar la pensión mensual al alumno")
)
# Create your models here.

class Pagos(models.Model):
	# Matricula = models.ForeignKey(Matricula,null=False,blank=False,on_delete=models.CASCADE)
	Dni = models.CharField(max_length=10,default='-')
	PagoMes = models.CharField(max_length=20,default='-')
	PagoAno = models.CharField(max_length=4,default='-')


class CronogramaPagos(models.Model):
	NumeroMes = models.IntegerField(_("Número del Mes"), null=False, blank=False,
							choices=[(3,"Marzo"),(4,"Abril"),(5,"Mayo"),(6,"Junio"),
				  				(7,"Julio"),(8,"Agosto"),(9,"Setiembre"),
								(10,"Octubre"),(11,"Noviembre"),(12,"Diciembre")])
	Matricula = models.ForeignKey(Matricula,blank=False,null=True,on_delete=models.PROTECT)
	cobrar_pension = models.BooleanField(_("Cobrar pensión"),default=True,
		help_text=_("Seleccione 'Sí' para cobrar la pensión mensual al alumno"))
	pagado = models.BooleanField("Pagado", default=False,help_text="Marque esta casilla si la pensión ha sido pagada")
	monto = models.DecimalField(_("Monto"), max_digits=8, decimal_places=2, default=0.00)
	observaciones = models.CharField(_("Observación"), max_length=100, blank=True, default="")
	created_at = models.DateTimeField(auto_now_add=True)
	update_at = models.DateTimeField(auto_now=True)


class MontoPension(models.Model):
    AnoAcademico = models.ForeignKey(AnoAcademico,null=False,blank=False,on_delete=models.PROTECT, verbose_name="Año Académico")    
    Monto = models.DecimalField("Monto de Pensión",max_digits=8, decimal_places=2, default=0.00,help_text="Monto establecido para la pensión este año")
    descripcion = models.CharField("Descripción",max_length=100, blank=True, default="",help_text="Ej: Pensión regular 2024")
    activo = models.BooleanField("Activo",default=True,help_text="Marcar si este es el monto activo para el año")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Monto de Pensión"
        verbose_name_plural = "Montos de Pensión"
        unique_together = ['AnoAcademico', 'activo']
        ordering = ['-AnoAcademico__Ano', '-activo']

    def __str__(self):
        return f"{self.AnoAcademico} - S/{self.Monto}"

    def save(self, *args, **kwargs):
        # Si se marca como activo, desactivar los demás montos del mismo año
        if self.activo:
            MontoPension.objects.filter(
                AnoAcademico=self.AnoAcademico
            ).exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_monto_activo(cls, ano_academico=None):
        """Obtener el monto activo para un año académico"""
        try:
            if ano_academico:
                return cls.objects.get(AnoAcademico=ano_academico, activo=True)
            else:
                # Buscar el año académico activo
                from .models import AnoAcademico
                ano_activo = AnoAcademico.get_ano_activo()
                if ano_activo:
                    return cls.objects.get(AnoAcademico=ano_activo, activo=True)
                return None
        except cls.DoesNotExist:
            return None


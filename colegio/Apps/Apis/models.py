from django.db import models

class Venta(models.Model):
    id_operation = models.IntegerField()
    id_persona = models.IntegerField()
    descripcion = models.CharField(max_length=150, null=True, blank=True)
    Dni = models.CharField(max_length=20, null=True, blank=True)
    Nombre = models.CharField(max_length=150, null=True, blank=True)
    Apellido = models.CharField(max_length=150, null=True, blank=True)
    NombreCompleto = models.CharField(max_length=400, null=True, blank=True)
    Nivel = models.CharField(max_length=100, null=True, blank=True)
    Grado = models.CharField(max_length=50, null=True, blank=True)
    Seccion = models.CharField(max_length=50, null=True, blank=True)
    Concepto = models.CharField(max_length=255, null=True, blank=True)
    Mes = models.CharField(max_length=20, null=True, blank=True)
    TipoIngreso = models.CharField(max_length=100, null=True, blank=True)
    ConceptoNumeroMes = models.CharField(max_length=100, null=True, blank=True)
    FechaVencimiento = models.CharField(max_length=20, null=True, blank=True)
    Monto = models.DecimalField(max_digits=10, decimal_places=2)
    FechaPago = models.CharField(max_length=20, null=True, blank=True)
    NumeroMesPago = models.IntegerField(null=True, blank=True)
    LetraMesPago = models.CharField(max_length=50, null=True, blank=True)
    Atrasado = models.CharField(max_length=50, null=True, blank=True)
    DiasAtraso = models.CharField(max_length=50, null=True, blank=True)
    MesesAtraso = models.CharField(max_length=50, null=True, blank=True)
    Apoderado = models.CharField(max_length=255, null=True, blank=True)
    Padre = models.CharField(max_length=255, null=True, blank=True)
    Madre = models.CharField(max_length=255, null=True, blank=True)
    Direccion = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.id_operation} - {self.NombreCompleto}"
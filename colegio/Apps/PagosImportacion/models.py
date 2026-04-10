from django.db import models

class ImportacionPagos(models.Model):
    """Registro de cada importación de Excel realizada"""
    fecha_importacion = models.DateTimeField(auto_now_add=True)
    nombre_archivo = models.CharField(max_length=255)
    total_registros = models.IntegerField(default=0)
    usuario = models.CharField(max_length=150, blank=True, null=True)
    anio = models.IntegerField(default=2026)
    
    class Meta:
        verbose_name = "Importación de Pagos"
        verbose_name_plural = "Importaciones de Pagos"
        ordering = ['-fecha_importacion']
    
    def __str__(self):
        return f"Importación {self.id} - {self.fecha_importacion.strftime('%Y-%m-%d %H:%M')}"

class PagoAlumno(models.Model):
    """Registro de pagos por alumno - Formato horizontal como el Excel"""
    
    # Datos del alumno
    num = models.IntegerField(blank=True, null=True)
    estudiante = models.CharField(max_length=255)
    dni = models.CharField(max_length=20, db_index=True, blank=True, null=True)
    doc_facturacion = models.CharField(max_length=50, blank=True, null=True)
    nombre_facturacion = models.CharField(max_length=255, blank=True, null=True)
    nivel = models.CharField(max_length=50)
    grado = models.CharField(max_length=10)
    seccion = models.CharField(max_length=10)
    
    # Pagos por mes (como viene en el Excel)
    marzo = models.CharField(max_length=100, blank=True, default='-')
    abril = models.CharField(max_length=100, blank=True, default='-')
    mayo = models.CharField(max_length=100, blank=True, default='-')
    junio = models.CharField(max_length=100, blank=True, default='-')
    julio = models.CharField(max_length=100, blank=True, default='-')
    agosto = models.CharField(max_length=100, blank=True, default='-')
    setiembre = models.CharField(max_length=100, blank=True, default='-')
    octubre = models.CharField(max_length=100, blank=True, default='-')
    noviembre = models.CharField(max_length=100, blank=True, default='-')
    diciembre = models.CharField(max_length=100, blank=True, default='-')
    
    # Totales
    total = models.CharField(max_length=100, blank=True, default='0')
    pagado = models.CharField(max_length=100, blank=True, default='0')
    
    # Metadatos
    importacion = models.ForeignKey(ImportacionPagos, on_delete=models.CASCADE, related_name='pagos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pago de Alumno"
        verbose_name_plural = "Pagos de Alumnos"
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['nivel', 'grado', 'seccion']),
        ]
    
    def __str__(self):
        return f"{self.estudiante} - {self.dni}"
    
    def get_valor_mes(self, mes):
        """Obtiene el valor de un mes específico"""
        meses = {
            'Marzo': self.marzo,
            'Abril': self.abril,
            'Mayo': self.mayo,
            'Junio': self.junio,
            'Julio': self.julio,
            'Agosto': self.agosto,
            'Setiembre': self.setiembre,
            'Octubre': self.octubre,
            'Noviembre': self.noviembre,
            'Diciembre': self.diciembre,
        }
        return meses.get(mes, '-')
    
    def esta_pagado_mes(self, mes):
        """Verifica si un mes está pagado"""
        valor = self.get_valor_mes(mes)
        if valor and valor != '-' and valor != 'NO' and '(DEBE)' not in valor:
            # Extraer si tiene monto numérico
            import re
            match = re.search(r'[\d,.]+', str(valor))
            if match:
                return float(match.group().replace(',', '')) > 0
        return False
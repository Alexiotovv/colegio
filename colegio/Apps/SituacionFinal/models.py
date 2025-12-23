from django.db import models
from django.core.exceptions import ValidationError
from colegio.Apps.Matricula.models import Matricula
import os
import zipfile
import rarfile
import tempfile
import PyPDF2
import re
from django.core.files.storage import FileSystemStorage
import traceback


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.zip', '.rar']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Solo se permiten archivos .zip o .rar')

class SituacionFinal(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, verbose_name="Matrícula")
    archivo_pdf = models.CharField(max_length=500, blank=True, null=True, verbose_name="PDF de origen")
    dni_encontrado = models.CharField(max_length=8, blank=True, null=True, verbose_name="DNI encontrado")
    situacion_final = models.CharField(max_length=100, blank=True, null=True, verbose_name="Situación Final")
    fecha_procesamiento = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Situación Final"
        verbose_name_plural = "Situaciones Finales"
        unique_together = ['matricula']
    
    def __str__(self):
        return f"{self.matricula} - {self.situacion_final}"

class ArchivoSituacionFinal(models.Model):
    archivo = models.FileField(
        upload_to='situacion_final/archivos/',
        validators=[validate_file_extension],
        verbose_name="Archivo ZIP/RAR"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False)
    total_procesados = models.IntegerField(default=0)
    total_errores = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Archivo de Situaciones Finales"
        verbose_name_plural = "Archivos de Situaciones Finales"
    
    def __str__(self):
        return f"Archivo {self.id} - {self.fecha_subida}"
    
    def extraer_y_procesar_pdfs(self):
        temp_dir = tempfile.mkdtemp()
        archivos_pdf = []
        
        # try:
            # Determinar si es ZIP o RAR
        if self.archivo.name.endswith('.zip'):
            with zipfile.ZipFile(self.archivo.path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        elif self.archivo.name.endswith('.rar'):
            with rarfile.RarFile(self.archivo.path, 'r') as rar_ref:
                rar_ref.extractall(temp_dir)
        
        # Buscar recursivamente archivos PDF
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    archivos_pdf.append(os.path.join(root, file))
        
        return archivos_pdf
            
        # except Exception as e:
        #     print(f"Error al extraer archivo: {e}")
        #     return []
    
    def buscar_dni_en_pdf(self, pdf_path):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Buscando DNI y situación en: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"PDF tiene {len(pdf_reader.pages)} páginas")
                
                if len(pdf_reader.pages) == 0:
                    logger.warning("PDF sin páginas")
                    return None, None
                
                # 1. BUSCAR DNI
                primera_pagina = pdf_reader.pages[0]
                texto_primera = primera_pagina.extract_text()
                
                if not texto_primera:
                    logger.warning("Primera página sin texto extraíble")
                    return None, None
                
                import re
                dni_match = re.search(r'DNI[:\s]*(\d{8})', texto_primera, re.IGNORECASE)
                
                if dni_match:
                    dni = dni_match.group(1)
                    logger.info(f"DNI encontrado: {dni}")
                else:
                    logger.warning("DNI no encontrado en primera página")
                    dni = None
                
                # 2. BUSCAR SITUACIÓN FINAL
                situacion = None
                situaciones_exactas = [
                    'Promovido de Grado',
                    'Requiere Recuperación', 
                    'Permanece en el Grado'
                ]
                
                for page_num, page in enumerate(pdf_reader.pages):
                    texto_pagina = page.extract_text()
                    
                    if not texto_pagina:
                        continue
                    
                    # Buscar "Situación al finalizar" en el texto
                    if 'Situación al finalizar' in texto_pagina:
                        logger.info(f"Encontrado 'Situación al finalizar' en página {page_num + 1}")
                        
                        # Buscar línea completa
                        lineas = texto_pagina.split('\n')
                        
                        for linea in lineas:
                            if 'Situación al finalizar' in linea:
                                logger.info(f"Línea encontrada: {linea[:100]}...")
                                
                                # Buscar las 3 opciones exactas
                                for situacion_exacta in situaciones_exactas:
                                    if situacion_exacta in linea:
                                        situacion = situacion_exacta
                                        logger.info(f"Situación encontrada: {situacion}")
                                        return dni, situacion
                        
                        # Si llegamos aquí, no encontró situación exacta
                        logger.warning("'Situación al finalizar' encontrada pero no la situación exacta")
                
                logger.warning(f"Situación no encontrada. DNI: {dni}")
                return dni, situacion
                
        except Exception as e:
            logger.error(f"Error en buscar_dni_en_pdf para {pdf_path}: {type(e).__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return None, None
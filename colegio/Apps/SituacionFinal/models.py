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
        
        try:
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
            
        except Exception as e:
            print(f"Error al extraer archivo: {e}")
            return []
    
    def buscar_dni_en_pdf(self, pdf_path):
        # try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) == 0:
                return None, None
            
            dni = None
            situacion = None
            
            # 1. BUSCAR DNI
            primera_pagina = pdf_reader.pages[0]
            texto_primera = primera_pagina.extract_text()
            
            if texto_primera:
                import re
                # Buscar cualquier número de 8 dígitos cerca de "DNI"
                dni_match = re.search(r'DNI[:\s]*(\d{8})', texto_primera, re.IGNORECASE)
                if dni_match:
                    dni = dni_match.group(1)
            
            # 2. BUSCAR SITUACIÓN FINAL - MÁS ROBUSTA
            # Analizar línea por línea
            for page_num, page in enumerate(pdf_reader.pages):
                texto_pagina = page.extract_text()
                
                if not texto_pagina:
                    continue
                
                # Dividir por líneas
                lineas = texto_pagina.split('\n')
                
                for linea in lineas:
                    # Buscar línea que contenga "Situación al finalizar"
                    if 'Situación al finalizar' in linea:
                        print(f"Línea encontrada: {linea}")
                        
                        # Dividir la línea para obtener la parte después de "Situación..."
                        partes = linea.split('Situación al finalizar el período lectivo')
                        if len(partes) > 1:
                            texto_despues = partes[1].strip()
                            
                            # Limpiar el texto
                            # Quitar posibles caracteres especiales al inicio
                            texto_despues = texto_despues.lstrip('|:;- ')
                            
                            # Tomar hasta el siguiente salto de línea implícito o 50 caracteres
                            situacion_candidato = texto_despues[:100].strip()
                            
                            # Buscar palabras clave en el candidato
                            palabras_clave = ['Promovido', 'Repite', 'Recuperación']
                            for palabra in palabras_clave:
                                if palabra in situacion_candidato:
                                    # Tomar la palabra clave y algunas palabras alrededor
                                    palabras = situacion_candidato.split()
                                    for i, palabra_linea in enumerate(palabras):
                                        if palabra in palabra_linea:
                                            # Tomar algunas palabras alrededor
                                            inicio = max(0, i-2)
                                            fin = min(len(palabras), i+3)
                                            situacion = ' '.join(palabras[inicio:fin])
                                            break
                                    if situacion:
                                        break
                            
                            if situacion:
                                break
                
                if situacion:
                    break
            
            return dni, situacion
                
        # except Exception as e:
        #     print(f"Error al procesar PDF {pdf_path}: {e}")
        #     import traceback
        #     traceback.print_exc()
        #     return None, None
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
        try:
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
                    dni_match = re.search(r'DNI[:\s]*(\d{8})', texto_primera, re.IGNORECASE)
                    if dni_match:
                        dni = dni_match.group(1)
                
                # 2. BUSCAR SITUACIÓN FINAL - BUSCAR LAS 3 OPCIONES EXACTAS
                for page in pdf_reader.pages:
                    texto_pagina = page.extract_text()
                    
                    if not texto_pagina:
                        continue
                    
                    # Buscar la línea completa que contiene "Situación al finalizar"
                    lineas = texto_pagina.split('\n')
                    
                    for linea in lineas:
                        if 'Situación al finalizar' in linea:
                            # DEBUG: Mostrar la línea completa
                            print(f"DEBUG - Línea completa: {linea}")
                            
                            # Buscar las 3 opciones exactas después de "Situación al finalizar el período lectivo"
                            # Definir las 3 situaciones exactas que buscamos
                            situaciones_exactas = [
                                'Promovido de Grado',
                                'Requiere Recuperación', 
                                'Permanece en el Grado'
                            ]
                            
                            # Intentar extraer la parte después de "Situación al finalizar el período lectivo"
                            if 'Situación al finalizar el período lectivo' in linea:
                                # Dividir la línea
                                partes = linea.split('Situación al finalizar el período lectivo')
                                texto_despues = partes[1].strip() if len(partes) > 1 else ""
                            else:
                                texto_despues = linea
                            
                            # Limpiar texto: eliminar "Página X de Y" y similares
                            texto_despues = re.sub(r'\s*Página\s*\d+\s*de\s*\d+.*', '', texto_despues, flags=re.IGNORECASE)
                            texto_despues = re.sub(r'\s*Pág\.\s*\d+.*', '', texto_despues, flags=re.IGNORECASE)
                            texto_despues = re.sub(r'\s*\d+\s*/\s*\d+.*', '', texto_despues)
                            
                            # Eliminar caracteres especiales al inicio
                            texto_despues = re.sub(r'^[|\-:\s]+', '', texto_despues)
                            
                            print(f"DEBUG - Texto después de limpiar: '{texto_despues}'")
                            
                            # Buscar coincidencia exacta con las 3 opciones
                            for situacion_exacta in situaciones_exactas:
                                # Verificar si la situación exacta está en el texto
                                if situacion_exacta in texto_despues:
                                    situacion = situacion_exacta
                                    print(f"DEBUG - Encontrado exacto: {situacion}")
                                    break
                            
                            # Si no encontró exacto, buscar por palabras clave completas
                            if not situacion:
                                # Buscar por inicio de cada opción
                                for situacion_exacta in situaciones_exactas:
                                    # Tomar las primeras 1-2 palabras de cada opción
                                    palabras_clave = situacion_exacta.split()[:2]
                                    clave_busqueda = ' '.join(palabras_clave)
                                    
                                    # Verificar si el texto comienza con estas palabras clave
                                    if texto_despues.startswith(clave_busqueda):
                                        # Contar cuántas palabras completas podemos tomar
                                        palabras_texto = texto_despues.split()
                                        palabras_situacion = situacion_exacta.split()
                                        
                                        # Tomar el número correcto de palabras
                                        if len(palabras_texto) >= len(palabras_situacion):
                                            situacion = situacion_exacta
                                        else:
                                            # Tomar todas las palabras disponibles
                                            situacion = ' '.join(palabras_texto[:len(palabras_situacion)])
                                        print(f"DEBUG - Encontrado por palabras clave: {situacion}")
                                        break
                            
                            # Si aún no tenemos situación, buscar coincidencias parciales
                            if not situacion:
                                palabras_despues = texto_despues.split()
                                
                                # Reconstruir la situación palabra por palabra
                                palabras_encontradas = []
                                
                                # Diccionario de mapeo completo
                                mapeo_completo = {
                                    'Promovido de Grado': ['Promovido', 'de', 'Grado'],
                                    'Requiere Recuperación': ['Requiere', 'Recuperación'],
                                    'Permanece en el Grado': ['Permanece', 'en', 'el', 'Grado']
                                }
                                
                                # Verificar cada situación
                                for situacion_exacta, palabras_esperadas in mapeo_completo.items():
                                    todas_encontradas = True
                                    palabras_candidato = []
                                    
                                    # Verificar si todas las palabras esperadas están en orden
                                    for palabra in palabras_esperadas:
                                        if palabra in palabras_despues:
                                            # Encontrar el índice de la palabra
                                            try:
                                                idx = palabras_despues.index(palabra)
                                                palabras_candidato.append(palabra)
                                            except:
                                                todas_encontradas = False
                                                break
                                        else:
                                            # Verificar si hay variaciones (plural, género, etc.)
                                            encontrada = False
                                            for p in palabras_despues:
                                                if palabra.lower() in p.lower():
                                                    palabras_candidato.append(palabra)  # Usar la palabra original
                                                    encontrada = True
                                                    break
                                            if not encontrada:
                                                todas_encontradas = False
                                                break
                                    
                                    if todas_encontradas and len(palabras_candidato) >= 2:
                                        # Reconstruir con las palabras originales esperadas
                                        situacion = situacion_exacta
                                        print(f"DEBUG - Reconstruido: {situacion}")
                                        break
                            
                            # Si encontramos situación, terminar
                            if situacion:
                                break
                    
                    if situacion:
                        break
                
                return dni, situacion
                
        except Exception as e:
            print(f"Error al procesar PDF {pdf_path}: {e}")
            import traceback
            traceback.print_exc()
            return None, None
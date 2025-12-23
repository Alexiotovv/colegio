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

        import tempfile
        import os
        import subprocess
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        # try:
            # Verificar que el archivo existe
        if not hasattr(self.archivo, 'path') or not os.path.exists(self.archivo.path):
            print(f"DEBUG: Archivo no existe: {getattr(self.archivo, 'path', 'No tiene path')}")
            return []
        
        # Solo procesar ZIP por ahora
        if not self.archivo.name.lower().endswith('.zip'):
            print(f"DEBUG: No es archivo ZIP: {self.archivo.name}")
            return []
        
        # Asegurar que 'unzip' está instalado
        # try:
        subprocess.run(['which', 'unzip'], check=True, capture_output=True)
        # except subprocess.CalledProcessError:
        #     print("DEBUG: Instalando unzip...")
        #     subprocess.run(['apt-get', 'update'], capture_output=True)
        #     subprocess.run(['apt-get', 'install', '-y', 'unzip'], capture_output=True)
        
        zip_path = self.archivo.path
        
        # PASO 1: Listar archivos en el ZIP
        # try:
        result = subprocess.run(
            ['unzip', '-l', zip_path],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            print(f"DEBUG: Error al listar ZIP: {result.stderr}")
            return []
        
        # Buscar PDFs en la lista
        pdf_files_in_zip = []
        for line in result.stdout.split('\n'):
            if '.pdf' in line.lower():
                # El nombre del archivo es la última columna
                parts = line.strip().split()
                if len(parts) >= 4:
                    filename = parts[-1]
                    if filename.lower().endswith('.pdf'):
                        pdf_files_in_zip.append(filename)
        
        print(f"DEBUG: PDFs encontrados en ZIP: {len(pdf_files_in_zip)}")
        
        if not pdf_files_in_zip:
            print("DEBUG: No hay PDFs en el archivo ZIP")
            return []
            
        # except Exception as e:
        #     print(f"DEBUG: Error al listar ZIP: {e}")
        #     return []
        
        # PASO 2: Extraer SOLO los PDFs
        archivos_pdf = []
        
        for pdf_file in pdf_files_in_zip:
            # try:
            # Crear nombre seguro para el archivo extraído
            safe_name = f"documento_{len(archivos_pdf)+1}.pdf"
            dest_path = os.path.join(temp_dir, safe_name)
            
            # Extraer archivo específico con unzip
            cmd = ['unzip', '-p', zip_path, pdf_file]
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                # Guardar el PDF
                with open(dest_path, 'wb') as f:
                    f.write(result.stdout)
                
                # Verificar que es un PDF válido
                if os.path.getsize(dest_path) > 100:  # Al menos 100 bytes
                    archivos_pdf.append(dest_path)
                    print(f"DEBUG: Extraído: {pdf_file} -> {safe_name}")
                else:
                    os.remove(dest_path)
            else:
                print(f"DEBUG: Error extrayendo {pdf_file}: {result.stderr}")
                    
            # except Exception as e:
            #     print(f"DEBUG: Error procesando {pdf_file}: {e}")
            #     continue
        
        print(f"DEBUG: Total PDFs extraídos: {len(archivos_pdf)}")
        return archivos_pdf
            
        # except Exception as e:
        #     print(f"DEBUG: Error general en extraer_y_procesar_pdfs: {e}")
        #     return []
        # finally:
        #     # Para debug, no eliminar temporalmente
        #     # shutil.rmtree(temp_dir, ignore_errors=True)
        #     pass
    
    # def extraer_y_procesar_pdfs(self):
    #     temp_dir = tempfile.mkdtemp()
    #     archivos_pdf = []
        
    #     try:
    #         # Determinar si es ZIP o RAR
    #         if self.archivo.name.endswith('.zip'):
    #             with zipfile.ZipFile(self.archivo.path, 'r') as zip_ref:
    #                 zip_ref.extractall(temp_dir)
    #         elif self.archivo.name.endswith('.rar'):
    #             with rarfile.RarFile(self.archivo.path, 'r') as rar_ref:
    #                 rar_ref.extractall(temp_dir)
            
    #         # Buscar recursivamente archivos PDF
    #         for root, dirs, files in os.walk(temp_dir):
    #             for file in files:
    #                 if file.lower().endswith('.pdf'):
    #                     archivos_pdf.append(os.path.join(root, file))
            
    #         return archivos_pdf
            
    #     except Exception as e:
    #         print(f"Error al extraer archivo: {e}")
    #         return []
    
    def buscar_dni_en_pdf(self, pdf_path):
        # try:
        import PyPDF2
        import re
        import sys
        
        print(f"DEBUG: Buscando en PDF: {pdf_path}")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) == 0:
                print("DEBUG: PDF sin páginas")
                return None, None
            
            dni = None
            situacion = None
            
            # BUSCAR DNI en primera página
            primera_pagina = pdf_reader.pages[0]
            texto_primera = primera_pagina.extract_text()
            
            if texto_primera:
                # Buscar DNI con diferentes patrones
                patrones_dni = [
                    r'DNI:\s*(\d{8})',
                    r'DNI\s*(\d{8})',
                    r'Documento:\s*(\d{8})',
                    r'D\.N\.I\.:\s*(\d{8})'
                ]
                
                for patron in patrones_dni:
                    match = re.search(patron, texto_primera, re.IGNORECASE)
                    if match:
                        dni = match.group(1)
                        print(f"DEBUG: DNI encontrado: {dni}")
                        break
            
            # BUSCAR SITUACIÓN en todas las páginas
            situaciones_buscar = [
                'Promovido de Grado',
                'Requiere Recuperación',
                'Permanece en el Grado'
            ]
            
            for page_num, page in enumerate(pdf_reader.pages):
                texto_pagina = page.extract_text()
                
                if not texto_pagina:
                    continue
                
                # Buscar línea con "Situación al finalizar"
                lineas = texto_pagina.split('\n')
                
                for linea in lineas:
                    if 'Situación al finalizar' in linea:
                        print(f"DEBUG: Encontrado 'Situación al finalizar' en página {page_num+1}")
                        print(f"DEBUG: Línea completa: {linea[:100]}...")
                        
                        # Buscar las situaciones exactas
                        for situacion_buscar in situaciones_buscar:
                            if situacion_buscar in linea:
                                situacion = situacion_buscar
                                print(f"DEBUG: Situación encontrada: {situacion}")
                                return dni, situacion
            
            print(f"DEBUG: Resultado - DNI: {dni}, Situación: {situacion}")
            return dni, situacion
                
        # except Exception as e:
        #     print(f"DEBUG: Error en buscar_dni_en_pdf: {e}")
        #     import traceback
        #     traceback.print_exc()
        #     return None, None
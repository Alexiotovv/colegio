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
    cursos = models.TextField(blank=True, null=True, verbose_name="Cursos con bajo rendimiento")
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
                    return None, None, None
                
                dni = None
                situacion = None
                cursos = None
                
                # 1. BUSCAR DNI
                primera_pagina = pdf_reader.pages[0]
                texto_primera = primera_pagina.extract_text()
                
                if texto_primera:
                    dni_match = re.search(r'DNI[:\s]*(\d{8})', texto_primera, re.IGNORECASE)
                    if dni_match:
                        dni = dni_match.group(1)
                
                # 2. PROCESAR TODAS LAS PÁGINAS
                for page in pdf_reader.pages:
                    texto_pagina = page.extract_text()
                    
                    if not texto_pagina:
                        continue
                    
                    # A. Buscar SITUACIÓN
                    if not situacion:
                        if 'Requiere Recuperación' in texto_pagina:
                            situacion = 'Requiere Recuperación'
                        elif 'Promovido' in texto_pagina:
                            situacion = 'Promovido'
                        elif 'Permanece en el Grado' in texto_pagina:
                            situacion = 'Permanece en el Grado'
                    
                    # B. Buscar CURSOS (solo si la situación es Recuperación)
                    if (situacion == 'Requiere Recuperación' or situacion == 'Permanece en el Grado') and not cursos:
                        frase_busqueda = 'Competencia(s) que no alcanzaron el nivel  de logro en las áreas o talleres'
                        
                        if frase_busqueda in texto_pagina:
                            print(f"DEBUG: Encontrada frase de competencias para {situacion}")
                            
                            # Buscar la posición de la frase
                            inicio = texto_pagina.find(frase_busqueda)
                            
                            if inicio != -1:
                                # Tomar texto después de la frase
                                texto_despues = texto_pagina[inicio + len(frase_busqueda):]
                                
                                # Si hay ":", tomar después de ":"
                                if ':' in texto_despues:
                                    texto_despues = texto_despues.split(':', 1)[1]
                                
                                # Dividir en líneas
                                lineas = texto_despues.split('\n')
                                
                                # Buscar la PRIMERA línea que NO sea paginado y SÍ sea curso
                                for linea in lineas:
                                    linea_limpia = linea.strip()
                                    
                                    # Saltar líneas vacías o muy cortas
                                    if not linea_limpia or len(linea_limpia) < 2:
                                        continue
                                    
                                    # Verificar si es curso de recuperación
                                    if self._es_curso_recuperacion(linea_limpia):
                                        cursos = linea_limpia
                                        print(f"DEBUG: Cursos identificados para {situacion}: {cursos}")    
                                        break
                    
                    # Si ya tenemos ambos, salir
                    if situacion and (cursos or situacion != 'Requiere Recuperación'):
                        break
                
                # 3. LIMPIAR PAGINADO DEL FINAL de los cursos (NUEVO)
                if cursos:
                    cursos = self._limpiar_paginado_final(cursos)
                    print(f"DEBUG: Cursos finales (después de limpiar): {cursos}")
                
                return dni, situacion, cursos
                
        except Exception as e:
            print(f"Error al procesar PDF {pdf_path}: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None

    def _limpiar_paginado_final(self, texto_cursos):
        """Limpia el paginado del final del texto de cursos"""
        if not texto_cursos:
            return texto_cursos
        
        # Lista de patrones de paginado a eliminar del final
        patrones_paginado = [
            'Página 1 de 4', 'Página 2 de 4', 'Página 3 de 4', 'Página 4 de 4',
        ]
        
        texto_limpio = texto_cursos
        
        # 1. Eliminar patrones completos
        for patron in patrones_paginado:
            # Buscar al final del texto
            if texto_limpio.endswith(patron):
                texto_limpio = texto_limpio[:-len(patron)].strip()
                print(f"DEBUG: Eliminado patrón completo: {patron}")
                break
        
        # 2. Eliminar cualquier "Página X de Y" al final usando regex
        # Buscar "Página" seguido de cualquier cosa hasta el final
        patron_regex = r'\s*Página\s+\d+\s+de\s+\d+\s*$'
        texto_limpio = re.sub(patron_regex, '', texto_limpio, flags=re.IGNORECASE)
        
        # 3. Eliminar "Pág. X de Y" o variantes
        patron_regex2 = r'\s*Pág\.?\s*\d+\s*[/-]\s*\d+\s*$'
        texto_limpio = re.sub(patron_regex2, '', texto_limpio, flags=re.IGNORECASE)
        
        # 4. Eliminar formato "X de Y" al final
        patron_regex3 = r'\s*\d+\s+de\s+\d+\s*$'
        texto_limpio = re.sub(patron_regex3, '', texto_limpio)
        
        # 5. Limpiar espacios extras y caracteres especiales residuales
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        
        # 6. Limpiar posibles guiones o puntos al final
        texto_limpio = texto_limpio.rstrip(' -.,;')
        
        return texto_limpio

    def _busqueda_alternativa_cursos(self, pdf_reader):
        """Búsqueda alternativa de cursos cuando el método principal falla"""
        frase_busqueda = 'Competencia(s) que no alcanzaron el nivel de logro'
        
        for page in pdf_reader.pages:
            texto_pagina = page.extract_text()
            
            if not texto_pagina or frase_busqueda not in texto_pagina:
                continue
            
            # Buscar después de la frase
            inicio = texto_pagina.find(frase_busqueda)
            if inicio == -1:
                continue
            
            # Tomar un segmento más grande (500 caracteres)
            segmento = texto_pagina[inicio:inicio + 500]
            
            # Buscar cursos en el segmento usando patrones más flexibles
            patrones = [
                r'(?:COMUNICACIÓN|MATEMÁTICA|INGLÉS|PERSONAL SOCIAL|EDUCACIÓN FÍSICA|CIENCIA Y TECNOLOGÍA)[\s\-]*(?:[\s\-]+(?:COMUNICACIÓN|MATEMÁTICA|INGLÉS|PERSONAL SOCIAL|EDUCACIÓN FÍSICA|CIENCIA Y TECNOLOGÍA))*',
                r'[A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ]+)*(?:\s*-\s*[A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ]+)*)+'
            ]
            
            for patron in patrones:
                match = re.search(patron, segmento, re.IGNORECASE)
                if match:
                    cursos = match.group(0).strip()
                    print(f"DEBUG: Cursos encontrados (alternativa): {cursos}")
                    return cursos
        
        return None

    def _es_curso_recuperacion(self, texto):
        """Identifica si el texto contiene cursos de recuperación"""
        if not texto:
            return False
        
        texto_upper = texto.upper()
        
        # Lista de cursos comunes de recuperación
        cursos_comunes = [
            'COMUNICACIÓN', 'MATEMÁTICA', 'INGLÉS', 'PERSONAL SOCIAL', 
            'EDUCACIÓN FÍSICA', 'CIENCIA', 'TECNOLOGÍA', 'HISTORIA',
            'GEOGRAFÍA', 'FORMACIÓN CIUDADANA', 'ARTE', 'RELIGIÓN',
            'TUTORÍA', 'COMPUTACIÓN', 'QUÍMICA', 'FÍSICA', 'BIOLOGÍA'
        ]
        
        # Patrones que indican cursos
        patrones_cursos = [
            r'[A-ZÁÉÍÓÚÑ]+\s*-',  # Palabra en mayúsculas seguida de guión
            r'\bCOMUNICACIÓN\b', r'\bMATEMÁTICA\b', r'\bINGLÉS\b',
            r'ÁREA\s+DE', r'TALLER\s+DE', r'CURSO\s+DE'
        ]
        
        # Verificar si contiene palabras clave de cursos
        for curso in cursos_comunes:
            if curso in texto_upper:
                return True
        
        # Verificar patrones de formato de cursos
        for patron in patrones_cursos:
            if re.search(patron, texto_upper):
                return True
        
        # Verificar si tiene formato de lista de cursos con guiones
        if '-' in texto and any(palabra in texto_upper for palabra in ['COMUNICACIÓN', 'MATEMÁTICA', 'INGLÉS']):
            return True
        
        return False


    # def buscar_dni_en_pdf(self, pdf_path):
    #     try:
    #         with open(pdf_path, 'rb') as file:
    #             pdf_reader = PyPDF2.PdfReader(file)
                
    #             if len(pdf_reader.pages) == 0:
    #                 return None, None, None
                
    #             dni = None
    #             situacion = None
    #             cursos = None
                
    #             # 1. BUSCAR DNI
    #             primera_pagina = pdf_reader.pages[0]
    #             texto_primera = primera_pagina.extract_text()
                
    #             if texto_primera:
    #                 dni_match = re.search(r'DNI[:\s]*(\d{8})', texto_primera, re.IGNORECASE)
    #                 if dni_match:
    #                     dni = dni_match.group(1)
                
    #             # 2. PROCESAR TODAS LAS PÁGINAS
    #             for page in pdf_reader.pages:
    #                 texto_pagina = page.extract_text()
                    
    #                 if not texto_pagina:
    #                     continue
                    
    #                 # A. Buscar SITUACIÓN
    #                 if not situacion:
    #                     # Buscar "Requiere Recuperación" directamente
    #                     if 'Requiere Recuperación' in texto_pagina:
    #                         situacion = 'Requiere Recuperación'
    #                     elif 'Promovido' in texto_pagina:
    #                         situacion = 'Promovido'
    #                     elif 'Permanece en el Grado' in texto_pagina:
    #                         situacion = 'Permanece en el Grado'
                    
    #                 # B. Buscar CURSOS (solo si la situación es Recuperación)
    #                 if situacion == 'Requiere Recuperación' and not cursos:
    #                     # Frase de búsqueda
    #                     frase_busqueda = 'Competencia(s) que no alcanzaron el nivel  de logro en las áreas o talleres'
    #                     print("Requiere Recuperación")
    #                     print("Imprimiendo texto de la página")
    #                     print(texto_pagina)
    #                     if frase_busqueda in texto_pagina:
    #                         print("encontroooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    #                         # Encontrar la posición de la frase
    #                         inicio = texto_pagina.find(frase_busqueda)
                            
    #                         if inicio != -1:
    #                             # Tomar texto después de la frase
    #                             texto_despues = texto_pagina[inicio + len(frase_busqueda):]
                                
    #                             # Buscar hasta el próximo salto de línea o límite
    #                             # Primero buscar ":"
    #                             if ':' in texto_despues:
    #                                 # Tomar después de ":"
    #                                 texto_despues = texto_despues.split(':', 1)[1]
                                
    #                             # Tomar los siguientes 100 caracteres (suficiente para cursos)
    #                             texto_cursos = texto_despues[:200].strip()
                                
    #                             # Limpiar: quitar líneas vacías, espacios extras
    #                             lineas_cursos = [linea.strip() for linea in texto_cursos.split('\n') 
    #                                         if linea.strip() and len(linea.strip()) > 1]
                                
    #                             if lineas_cursos:
    #                                 # Tomar la primera línea no vacía después de la frase
    #                                 cursos = lineas_cursos[0]
                                    
    #                                 # Limpiar caracteres especiales
    #                                 cursos = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ\-]', ' ', cursos)
    #                                 cursos = re.sub(r'\s+', ' ', cursos).strip()
                    
    #                 # Si ya tenemos ambos, salir
    #                 if situacion and (cursos or situacion != 'Requiere Recuperación'):
    #                     break
                
    #             return dni, situacion, cursos
                
    #     except Exception as e:
    #         print(f"Error al procesar PDF {pdf_path}: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         return None, None, None

    # def buscar_dni_en_pdf(self, pdf_path):
    #     # try:
    #     with open(pdf_path, 'rb') as file:
    #         pdf_reader = PyPDF2.PdfReader(file)
            
    #         if len(pdf_reader.pages) == 0:
    #             return None, None
            
    #         dni = None
    #         situacion = None
            
    #         # 1. BUSCAR DNI
    #         primera_pagina = pdf_reader.pages[0]
    #         texto_primera = primera_pagina.extract_text()
            
    #         if texto_primera:
    #             import re
    #             # Buscar cualquier número de 8 dígitos cerca de "DNI"
    #             dni_match = re.search(r'DNI[:\s]*(\d{8})', texto_primera, re.IGNORECASE)
    #             if dni_match:
    #                 dni = dni_match.group(1)
            
    #         # 2. BUSCAR SITUACIÓN FINAL - MÁS ROBUSTA
    #         # Analizar línea por línea
    #         for page_num, page in enumerate(pdf_reader.pages):
    #             texto_pagina = page.extract_text()
                
    #             if not texto_pagina:
    #                 continue
                
    #             # Dividir por líneas
    #             lineas = texto_pagina.split('\n')
                
    #             for linea in lineas:
    #                 # Buscar línea que contenga "Situación al finalizar"
    #                 if 'Situación al finalizar' in linea:
    #                     print(f"Línea encontrada: {linea}")
                        
    #                     # Dividir la línea para obtener la parte después de "Situación..."
    #                     partes = linea.split('Situación al finalizar el período lectivo')
    #                     if len(partes) > 1:
    #                         texto_despues = partes[1].strip()
                            
    #                         # Limpiar el texto
    #                         # Quitar posibles caracteres especiales al inicio
    #                         texto_despues = texto_despues.lstrip('|:;- ')
                            
    #                         # Tomar hasta el siguiente salto de línea implícito o 50 caracteres
    #                         situacion_candidato = texto_despues[:100].strip()
                            
    #                         # Buscar palabras clave en el candidato
    #                         palabras_clave = ['Promovido', 'Repite', 'Recuperación']
    #                         for palabra in palabras_clave:
    #                             if palabra in situacion_candidato:
    #                                 # Tomar la palabra clave y algunas palabras alrededor
    #                                 palabras = situacion_candidato.split()
    #                                 for i, palabra_linea in enumerate(palabras):
    #                                     if palabra in palabra_linea:
    #                                         # Tomar algunas palabras alrededor
    #                                         inicio = max(0, i-2)
    #                                         fin = min(len(palabras), i+3)
    #                                         situacion = ' '.join(palabras[inicio:fin])
    #                                         break
    #                                 if situacion:
    #                                     break
                            
    #                         if situacion:
    #                             break
                
    #             if situacion:
    #                 break
            
    #         return dni, situacion
                
    #     # except Exception as e:
    #     #     print(f"Error al procesar PDF {pdf_path}: {e}")
    #     #     import traceback
    #     #     traceback.print_exc()
    #     #     return None, None
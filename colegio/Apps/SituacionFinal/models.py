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
                
                # 2. BUSCAR SITUACIÓN
                for page in pdf_reader.pages:
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        if 'Requiere Recuperación' in texto_pagina:
                            situacion = 'Requiere Recuperación'
                            break
                        elif 'Promovido' in texto_pagina:
                            situacion = 'Promovido'
                            break
                        elif 'Permanece en el Grado' in texto_pagina:
                            situacion = 'Permanece en el Grado'
                            break
                
                # 3. BUSCAR CURSOS (SOLO desde página 3 en adelante)
                if situacion in ['Requiere Recuperación', 'Permanece en el Grado']:
                    # Empezar desde la página 3 (índice 2)
                    for page_num in range(2, len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        texto_pagina = page.extract_text()
                        
                        if not texto_pagina:
                            continue
                        
                        print(f"DEBUG: Buscando cursos en página {page_num + 1}")
                        
                        # Usar la nueva función que maneja cursos específicos
                        cursos_encontrados = self._buscar_cursos_en_texto(texto_pagina)
                        
                        if cursos_encontrados:
                            cursos = cursos_encontrados
                            print(f"DEBUG: Cursos encontrados: {cursos}")
                            
                            # Limpiar paginado
                            cursos = self._limpiar_paginado_final(cursos)
                            break
                
                return dni, situacion, cursos
                
        except Exception as e:
            print(f"Error al procesar PDF {pdf_path}: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None



    def _buscar_cursos_en_texto(self, texto_pagina):
        """
        Versión simplificada que maneja líneas rotas
        """
        if not texto_pagina:
            return None
        
        # 1. Primero reemplazar saltos de línea problemáticos
        # Unir "EDUCACIÓN\nFÍSICA" → "EDUCACIÓN FÍSICA"
        # Unir "EDUCACIÓN\nRELIGIOSA" → "EDUCACIÓN RELIGIOSA"
        
        texto_arreglado = texto_pagina
        
        # Patrones comunes de cursos divididos
        patrones_unir = [
            (r'EDUCACIÓN\s*\n\s*FÍSICA', 'EDUCACIÓN FÍSICA'),
            (r'EDUCACIÓN\s*\n\s*RELIGIOSA', 'EDUCACIÓN RELIGIOSA'),
            (r'ARTE\s+Y\s*\n\s*CULTURA', 'ARTE Y CULTURA'),
            (r'CIENCIA\s+Y\s*\n\s*TECNOLOGÍA', 'CIENCIA Y TECNOLOGÍA'),
            (r'DESARROLLO\s+PERSONAL,\s+CIUDADANÍA\s+Y\s*\n\s*CÍVICA', 'DESARROLLO PERSONAL, CIUDADANÍA Y CÍVICA'),
        ]
        
        for patron, reemplazo in patrones_unir:
            texto_arreglado = re.sub(patron, reemplazo, texto_arreglado, flags=re.IGNORECASE)
        
        # 2. Buscar lista de cursos separados por guiones
        texto_upper = texto_arreglado.upper()
        
        # Patrón para encontrar listas de cursos: texto en mayúsculas con guiones
        patron_lista = r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,\-]+(?:\s*-\s*[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,\-]+)+)'
        matches = re.findall(patron_lista, texto_upper)
        
        if matches:
            # Tomar la lista más larga
            lista_mas_larga = max(matches, key=len)
            
            # Buscar en el texto original (con las correcciones)
            pos = texto_upper.find(lista_mas_larga)
            if pos != -1:
                cursos_texto = texto_arreglado[pos:pos + len(lista_mas_larga)].strip()
                
                # Separar por guiones y limpiar
                partes = [p.strip() for p in cursos_texto.split('-')]
                
                # Post-procesar: unir "EDUCACIÓN" con "FÍSICA" o "RELIGIOSA"
                partes_finales = []
                i = 0
                
                while i < len(partes):
                    if i + 1 < len(partes):
                        # Si encontramos "EDUCACIÓN" seguido de "FÍSICA"
                        if (partes[i].upper() == "EDUCACIÓN" and 
                            partes[i + 1].upper() == "FÍSICA"):
                            partes_finales.append("EDUCACIÓN FÍSICA")
                            i += 2
                            continue
                        
                        # Si encontramos "EDUCACIÓN" seguido de "RELIGIOSA"
                        elif (partes[i].upper() == "EDUCACIÓN" and 
                            partes[i + 1].upper() == "RELIGIOSA"):
                            partes_finales.append("EDUCACIÓN RELIGIOSA")
                            i += 2
                            continue
                    
                    # Agregar la parte normal
                    partes_finales.append(partes[i])
                    i += 1
                
                # Filtrar cursos válidos
                cursos_validos = [
                    "INGLÉS COMO LENGUA EXTRANJERA",
                    "PERSONAL SOCIAL",
                    "DESARROLLO PERSONAL, CIUDADANÍA Y CÍVICA",
                    "CIENCIAS SOCIALES",
                    "EDUCACIÓN FÍSICA",
                    "ARTE Y CULTURA",
                    "COMUNICACIÓN",
                    "INGLÉS",
                    "MATEMÁTICA",
                    "CIENCIA Y TECNOLOGÍA",
                    "EDUCACIÓN RELIGIOSA",
                    "EDUCACIÓN PARA EL TRABAJO",
                    "IDIOMA CHINO MANDARÍN"
                ]
                
                # Filtrar solo cursos válidos
                cursos_filtrados = []
                for curso in partes_finales:
                    if any(curso_valido in curso.upper() for curso_valido in cursos_validos):
                        cursos_filtrados.append(curso)
                
                if cursos_filtrados:
                    # Limpiar "Firma del Docente o Tutor" del último curso
                    cursos_finales_limpios = []
                    
                    for curso in cursos_filtrados:
                        # Buscar "Firma del Docente o" en el curso
                        pos_firma = curso.upper().find('FIRMA DEL DOCENTE O')
                        if pos_firma != -1:
                            # Cortar el texto antes de "Firma del Docente o"
                            curso_limpio = curso[:pos_firma].strip()
                            # También limpiar si queda un guión o coma al final
                            curso_limpio = curso_limpio.rstrip(' ,-')
                            cursos_finales_limpios.append(curso_limpio)
                        else:
                            cursos_finales_limpios.append(curso)
                    
                    # Actualizar cursos_filtrados con los limpiados
                    cursos_filtrados = cursos_finales_limpios
                    
                    # También verificar si el último curso termina con esos textos
                    if cursos_filtrados:
                        ultimo_curso = cursos_filtrados[-1]
                        # Patrones a eliminar del final
                        patrones_firma = [
                            'Firma del Docente o',
                            'Firma del Tutor',
                            'Firma del Director',
                            'Firma:'
                        ]
                        
                        for patron in patrones_firma:
                            if patron in ultimo_curso:
                                # Encontrar la posición
                                pos = ultimo_curso.find(patron)
                                ultimo_curso = ultimo_curso[:pos].strip()
                                ultimo_curso = ultimo_curso.rstrip(' ,-')
                                cursos_filtrados[-1] = ultimo_curso
                                break
                
                if cursos_filtrados:
                    return ' - '.join(cursos_filtrados)
        
        return None

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

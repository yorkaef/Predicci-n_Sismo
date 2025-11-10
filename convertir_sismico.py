import os
import csv
import re
from pathlib import Path

def extraer_datos_estacion(lineas):
    """Extrae información de la estación sísmica"""
    estacion = {}
    for linea in lineas:
        if 'NOMBRE' in linea and 'ESTACION' in linea:
            match = re.search(r'NOMBRE\s*:\s*(.+)', linea)
            if match:
                estacion['nombre'] = match.group(1).strip()
        elif 'CODIGO' in linea:
            match = re.search(r'CODIGO\s*:\s*(.+)', linea)
            if match:
                estacion['codigo'] = match.group(1).strip()
        elif 'LATITUD' in linea and 'ESTACION' in lineas[0]:
            match = re.search(r'LATITUD\s*:\s*([-\d.]+)', linea)
            if match:
                estacion['latitud_estacion'] = match.group(1).strip()
        elif 'LONGITUD' in linea and 'ESTACION' in lineas[0]:
            match = re.search(r'LONGITUD\s*:\s*([-\d.]+)', linea)
            if match:
                estacion['longitud_estacion'] = match.group(1).strip()
    return estacion

def extraer_datos_sismo(lineas):
    """Extrae información del sismo"""
    sismo = {}
    for linea in lineas:
        if 'FECHA LOCAL' in linea:
            match = re.search(r'FECHA LOCAL\s*:\s*(.+)', linea)
            if match:
                sismo['fecha_local'] = match.group(1).strip()
        elif 'HORA LOCAL' in linea:
            match = re.search(r'HORA LOCAL\s*:\s*(.+)', linea)
            if match:
                sismo['hora_local'] = match.group(1).strip()
        elif 'LATITUD' in linea and 'SISMO' in lineas[0]:
            match = re.search(r'LATITUD\s*:\s*([-\d.]+)', linea)
            if match:
                sismo['latitud_sismo'] = match.group(1).strip()
        elif 'LONGITUD' in linea and 'SISMO' in lineas[0]:
            match = re.search(r'LONGITUD\s*:\s*([-\d.]+)', linea)
            if match:
                sismo['longitud_sismo'] = match.group(1).strip()
        elif 'PROFUNDIDAD' in linea:
            match = re.search(r'PROFUNDIDAD\s*:\s*([\d.]+)', linea)
            if match:
                sismo['profundidad'] = match.group(1).strip()
        elif 'MAGNITUD' in linea:
            match = re.search(r'MAGNITUD\s*:\s*(.+)', linea)
            if match:
                sismo['magnitud'] = match.group(1).strip()
        elif 'DIST. EPICENTRAL' in linea or 'DIST.EPICENTRAL' in linea:
            match = re.search(r'DIST\.\s*EPICENTRAL\s*:\s*([\d.]+)', linea)
            if match:
                sismo['dist_epicentral'] = match.group(1).strip()
    return sismo

def extraer_datos_registro(lineas):
    """Extrae información del registro"""
    registro = {}
    for linea in lineas:
        if 'TIEMPO DE INICIO' in linea:
            match = re.search(r'TIEMPO DE INICIO\s*:\s*(.+)', linea)
            if match:
                registro['tiempo_inicio'] = match.group(1).strip()
        elif 'NUMERO DE MUESTRAS' in linea:
            match = re.search(r'NUMERO DE MUESTRAS\s*:\s*(\d+)', linea)
            if match:
                registro['num_muestras'] = match.group(1).strip()
        elif 'MUESTREO' in linea:
            match = re.search(r'MUESTREO\s*:\s*(.+)', linea)
            if match:
                registro['muestreo'] = match.group(1).strip()
        elif 'UNIDADES' in linea:
            match = re.search(r'UNIDADES\s*:\s*(.+)', linea)
            if match:
                registro['unidades'] = match.group(1).strip()
        elif 'PGA' in linea:
            match = re.search(r'PGA\s*:\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)', linea)
            if match:
                registro['pga_z'] = match.group(1).strip()
                registro['pga_n'] = match.group(2).strip()
                registro['pga_e'] = match.group(3).strip()
    return registro

def procesar_archivo_txt(ruta_txt):
    """Procesa un archivo TXT y extrae toda la información"""
    try:
        with open(ruta_txt, 'r', encoding='utf-8', errors='ignore') as f:
            contenido = f.read()
        
        lineas = contenido.split('\n')
        
        # Buscar secciones
        seccion_estacion = []
        seccion_sismo = []
        seccion_registro = []
        datos_aceleracion = []
        
        seccion_actual = None
        capturando_datos = False
        
        for i, linea in enumerate(lineas):
            linea_upper = linea.upper()
            
            if 'ESTACION SISMICA' in linea_upper or 'ESTACIÓN SÍSMICA' in linea_upper:
                seccion_actual = 'estacion'
                capturando_datos = False
            elif 'SISMO' in linea_upper and 'ESTACION' not in linea_upper:
                seccion_actual = 'sismo'
                capturando_datos = False
            elif 'REGISTRO' in linea_upper:
                seccion_actual = 'registro'
                capturando_datos = False
            elif 'Z N E' in linea or (seccion_actual == 'registro' and re.match(r'^\s*[-\d.]+\s+[-\d.]+\s+[-\d.]+\s*$', linea)):
                capturando_datos = True
                if 'Z N E' not in linea:
                    datos_aceleracion.append(linea.strip())
                continue
            
            if seccion_actual == 'estacion' and not capturando_datos:
                seccion_estacion.append(linea)
            elif seccion_actual == 'sismo' and not capturando_datos:
                seccion_sismo.append(linea)
            elif seccion_actual == 'registro' and not capturando_datos:
                seccion_registro.append(linea)
            elif capturando_datos and linea.strip():
                datos_aceleracion.append(linea.strip())
        
        # Extraer datos de cada sección
        info_estacion = extraer_datos_estacion(seccion_estacion)
        info_sismo = extraer_datos_sismo(seccion_sismo)
        info_registro = extraer_datos_registro(seccion_registro)
        
        # Combinar toda la información
        info_completa = {**info_estacion, **info_sismo, **info_registro}
        
        # Procesar datos de aceleración
        registros = []
        for linea in datos_aceleracion:
            partes = linea.split()
            if len(partes) >= 3:
                try:
                    registro = info_completa.copy()
                    registro['acel_z'] = partes[0]
                    registro['acel_n'] = partes[1]
                    registro['acel_e'] = partes[2]
                    registros.append(registro)
                except:
                    continue
        
        return registros
    
    except Exception as e:
        print(f"Error procesando {ruta_txt}: {str(e)}")
        return []

def convertir_txt_a_csv(carpeta_raiz, carpeta_salida='csv'):
    """Convierte todos los archivos TXT a CSV manteniendo la estructura de carpetas"""
    
    # Crear carpeta de salida si no existe
    Path(carpeta_salida).mkdir(parents=True, exist_ok=True)
    
    # Buscar todos los archivos TXT
    archivos_txt = list(Path(carpeta_raiz).rglob('*.txt'))
    
    print(f"Encontrados {len(archivos_txt)} archivos TXT")
    print(f"Carpeta raíz: {carpeta_raiz}")
    print(f"Carpeta salida: {carpeta_salida}\n")
    
    carpetas_procesadas = set()
    archivos_procesados = 0
    
    for archivo_txt in archivos_txt:
        print(f"Procesando: {archivo_txt}")
        
        # Obtener la carpeta padre del archivo TXT
        carpeta_padre = archivo_txt.parent.name
        carpetas_procesadas.add(carpeta_padre)
        
        # Crear la misma estructura de carpetas en la salida
        carpeta_destino = Path(carpeta_salida) / carpeta_padre
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        # Procesar archivo
        registros = procesar_archivo_txt(archivo_txt)
        
        if not registros:
            print(f"  → No se pudieron extraer datos")
            continue
        
        # Crear nombre del CSV
        nombre_csv = archivo_txt.stem + '.csv'
        ruta_csv = carpeta_destino / nombre_csv
        
        # Escribir CSV
        if registros:
            campos = list(registros[0].keys())
            
            with open(ruta_csv, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(registros)
            
            archivos_procesados += 1
            print(f"  ✓ Creado: {ruta_csv} ({len(registros)} registros)")
    
    print(f"\n{'='*60}")
    print(f"✓ Conversión completada")
    print(f"  Carpetas procesadas: {len(carpetas_procesadas)}")
    print(f"  Archivos convertidos: {archivos_procesados}")
    print(f"  Ubicación: {carpeta_salida}/")
    print(f"{'='*60}")
    
    # Mostrar estructura creada
    print(f"\nEstructura de carpetas creada:")
    for carpeta in sorted(carpetas_procesadas):
        num_archivos = len(list((Path(carpeta_salida) / carpeta).glob('*.csv')))
        print(f"  📁 {carpeta}/ ({num_archivos} archivos CSV)")

# ============================================
# EJECUTAR CONVERSIÓN
# ============================================

if __name__ == "__main__":
    # Configuración
    CARPETA_RAIZ = "2021"  # Cambia esto a tu carpeta raíz con los TXT
    CARPETA_SALIDA = "2021_csv"      # Carpeta donde se guardarán los CSV organizados
    
    # Ejecutar conversión
    convertir_txt_a_csv(CARPETA_RAIZ, CARPETA_SALIDA)
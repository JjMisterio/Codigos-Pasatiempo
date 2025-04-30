import re

# Expresión regular mejorada para detectar fechas incorrectas
patron_fecha = re.compile(r"\b(\d{4})(\d{2})(\d{2})\b|\b(\d{2})[-/](\d{2})[-/](\d{4})\b")

def corregir_fecha(fecha):
    """ Corrige fechas de diferentes formatos al estándar YYYY-MM-DD HH:MM:SS si aplica. """
    if re.match(r"\d{4}\d{2}\d{2}", fecha):  # Formato YYYYMMDD
        return f"{fecha[:4]}-{fecha[4:6]}-{fecha[6:8]}"
    elif re.match(r"\d{2}[-/]\d{2}[-/]\d{4}", fecha):  # Formato DD/MM/YYYY o DD-MM-YYYY
        partes = re.split(r"[-/]", fecha)
        return f"{partes[2]}-{partes[1]}-{partes[0]}"
    return fecha  # No modificar si ya está correcto

# Leer el archivo SQL y modificar fechas incorrectas
archivo_sql = "R22+INSERT+PedidosEncargos.sql"  # Nombre del archivo original
archivo_corregido = "datos_corregidos.sql"

with open(archivo_sql, "r", encoding="ISO-8859-1") as f:
    lineas = f.readlines()

lineas_modificadas = []
modificado = False
print("--- Iniciando búsqueda de fechas ---") # Mensaje de depuración

for i, linea in enumerate(lineas): # Añade enumerate para saber el número de línea
    linea_original = linea # Guarda la línea original para comparar
    fechas_encontradas = patron_fecha.findall(linea)

    if fechas_encontradas: # Imprime solo si encuentra algo en la línea
        print(f"Línea {i+1}: Posibles fechas encontradas: {fechas_encontradas}")

    for fecha_tuple in fechas_encontradas:
        # Extrae la cadena relevante (ignora los grupos vacíos)
        fecha_str_parts = [part for part in fecha_tuple if part]
        if len(fecha_str_parts) == 3: # Asegura que tenemos 3 partes (YYYY, MM, DD) o (DD, MM, YYYY)
            # Reconstruye la cadena original encontrada por el regex
            if fecha_tuple[0]: # Formato YYYYMMDD
                fecha_str = "".join(fecha_tuple[0:3])
            else: # Formato DD/MM/YYYY
                 # Necesitamos el separador original para reemplazarlo correctamente
                 # Usamos re.search para obtener el match object y la cadena completa
                 match = re.search(r"\b(\d{2}([-/])\d{2}\2\d{4})\b", linea) # Busca el formato completo
                 if match:
                     fecha_str = match.group(1) # Obtiene la fecha completa ej: '15/05/2023'
                 else:
                     # Fallback por si search falla (poco probable si findall funcionó)
                     fecha_str = f"{fecha_tuple[3]}{'/'}{fecha_tuple[4]}{'/'}{fecha_tuple[5]}" # Asume / como separador

            print(f"  Procesando tupla: {fecha_tuple} -> Extraído: '{fecha_str}'") # Mensaje de depuración
            fecha_formateada = corregir_fecha(fecha_str)
            print(f"    Resultado de corregir_fecha: '{fecha_formateada}'") # Mensaje de depuración

            if fecha_str != fecha_formateada:
                print(f"    ¡Reemplazo necesario! Reemplazando '{fecha_str}' por '{fecha_formateada}'") # Mensaje de depuración
                linea = linea.replace(fecha_str, fecha_formateada, 1) # Reemplaza solo la primera ocurrencia para evitar problemas si la misma fecha aparece más veces
                modificado = True
        else:
             print(f"  Ignorando tupla inválida o inesperada: {fecha_tuple}")


    if linea_original != linea:
         print(f"  Línea {i+1} modificada.") # Mensaje de depuración

    lineas_modificadas.append(linea)

print("--- Búsqueda de fechas terminada ---") # Mensaje de depuración

# Guardar solo si hubo modificaciones
if modificado:
    with open(archivo_corregido, "w", encoding="utf-8") as f:
        f.writelines(lineas_modificadas)
    print(f"Corrección completada. Archivo guardado como {archivo_corregido}.")
else:
    print("No se encontraron fechas para corregir en el archivo.")

import requests
import csv
import time

def get_travel_time(origin_coords, destination_coords):
    """
    Calcula el tiempo de viaje estimado en coche entre dos puntos usando OSRM.
    Devuelve el tiempo en segundos.
    """
    if not origin_coords or not destination_coords:
        return None

    # Formato para OSRM: lon,lat;lon,lat
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_coords[1]},{origin_coords[0]};{destination_coords[1]},{destination_coords[0]}?overview=false"
    
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()  # Lanza un error para respuestas HTTP malas (4xx o 5xx)
        data = response.json()
        
        if data['code'] == 'Ok' and data['routes']:
            # La duración está en segundos
            return data['routes'][0]['duration'] 
        else:
            print(f"OSRM no pudo encontrar una ruta: {data.get('message', 'No message')}")
            return None
    except requests.exceptions.Timeout:
        print(f"Timeout al contactar OSRM para {origin_coords} -> {destination_coords}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a OSRM para {origin_coords} -> {destination_coords}: {e}")
        return None
    except Exception as e:
        print(f"Error desconocido procesando respuesta de OSRM para {origin_coords} -> {destination_coords}: {e}")
        return None

def format_duration(seconds):
    """Convierte segundos a un formato legible HH:MM:SS o MM:SS."""
    if seconds is None:
        return "N/A"
    try:
        seconds = float(seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
        else:
            return f"{minutes:02d}m {secs:02d}s"
    except (ValueError, TypeError):
        return "Error en formato"


if __name__ == "__main__":
    # Leer coordenadas de origen
    try:
        with open("origin_coords.txt", "r") as f:
            lat_str, lon_str = f.read().strip().split(',')
            origin_coords = (float(lat_str), float(lon_str))
        print(f"Coordenadas de origen cargadas: {origin_coords}")
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'origin_coords.txt'. Ejecuta get_coordinates.py primero para la dirección de origen.")
        exit()
    except ValueError:
        print("Error: El formato de 'origin_coords.txt' es incorrecto.")
        exit()

    # Leer coordenadas de municipios
    municipios_data = []
    try:
        with open("municipios_coords.csv", "r", encoding="utf-8") as f_csv:
            reader = csv.DictReader(f_csv)
            if not reader.fieldnames or not all(col in reader.fieldnames for col in ["Municipio", "Latitud", "Longitud"]):
                print("Error: El archivo 'municipios_coords.csv' no tiene las columnas esperadas (Municipio, Latitud, Longitud).")
                exit()
            for row in reader:
                municipios_data.append(row)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'municipios_coords.csv'. Ejecuta get_coordinates.py primero para los municipios.")
        exit()
    
    if not municipios_data:
        print("No hay datos de municipios en 'municipios_coords.csv'.")
        exit()

    print(f"Procesando tiempos de viaje para {len(municipios_data)} municipios...")
    
    results = []
    for i, data in enumerate(municipios_data):
        municipio_nombre = data["Municipio"]
        lat_str = data["Latitud"]
        lon_str = data["Longitud"]

        if lat_str == "None" or lon_str == "None" or not lat_str or not lon_str:
            print(f"[{i+1}/{len(municipios_data)}] Coordenadas no disponibles para {municipio_nombre}. Saltando.")
            results.append({"Municipio": municipio_nombre, "Tiempo de Viaje (s)": None, "Tiempo Formateado": "N/A"})
            continue
        
        try:
            destination_coords = (float(lat_str), float(lon_str))
        except ValueError:
            print(f"[{i+1}/{len(municipios_data)}] Formato de coordenadas incorrecto para {municipio_nombre}: Lat={lat_str}, Lon={lon_str}. Saltando.")
            results.append({"Municipio": municipio_nombre, "Tiempo de Viaje (s)": None, "Tiempo Formateado": "N/A"})
            continue

        print(f"[{i+1}/{len(municipios_data)}] Calculando tiempo para {municipio_nombre} ({destination_coords})...")
        travel_time_seconds = get_travel_time(origin_coords, destination_coords)
        
        if travel_time_seconds is not None:
            print(f"Tiempo para {municipio_nombre}: {travel_time_seconds:.0f} segundos ({format_duration(travel_time_seconds)})")
            results.append({
                "Municipio": municipio_nombre, 
                "Tiempo de Viaje (s)": travel_time_seconds,
                "Tiempo Formateado": format_duration(travel_time_seconds)
            })
        else:
            print(f"No se pudo obtener el tiempo de viaje para {municipio_nombre}.")
            results.append({
                "Municipio": municipio_nombre, 
                "Tiempo de Viaje (s)": None,
                "Tiempo Formateado": "N/A"
            })
        
        time.sleep(1.1) # Pausa para no sobrecargar la API pública de OSRM (límite ~1 req/s)

    # Ordenar por tiempo de viaje (los None/N/A irán al final o principio dependiendo de la implementación de sort)
    # Para asegurar que los 'None' vayan al final, usamos una clave de ordenación
    results.sort(key=lambda x: (x["Tiempo de Viaje (s)"] is None, x["Tiempo de Viaje (s)"]))

    # Guardar resultados en CSV
    output_filename = "tiempos_viaje_municipios.csv"
    try:
        with open(output_filename, "w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=["Municipio", "Tiempo de Viaje (s)", "Tiempo Formateado"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Resultados guardados en '{output_filename}'")
    except IOError:
        print(f"Error al escribir el archivo '{output_filename}'")

    # Limpiar archivos intermedios si es necesario (o mantenerlos para depuración)
    # import os
    # os.remove("origin_coords.txt")
    # os.remove("municipios_coords.csv")
    # print("Archivos intermedios eliminados.")

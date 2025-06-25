from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_coords(address):
    """
    Obtiene las coordenadas (latitud, longitud) para una dirección dada.
    """
    geolocator = Nominatim(user_agent="malaga_municipios_app")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"No se encontraron coordenadas para: {address}")
            return None
    except GeocoderTimedOut:
        print(f"Error de tiempo de espera al geocodificar: {address}")
        return None
    except GeocoderUnavailable:
        print(f"Servicio de geocodificación no disponible para: {address}")
        return None
    except Exception as e:
        print(f"Error desconocido al geocodificar {address}: {e}")
        return None

import time

if __name__ == "__main__":
    # Coordenadas de Origen (ya obtenidas y guardadas)
    # origin_address = "Calle Viña del Mar 10, 29004 Málaga, Spain"
    # origin_coords = get_coords(origin_address)
    #
    # if origin_coords:
    #     print(f"Coordenadas de Origen ({origin_address}): {origin_coords}")
    #     with open("origin_coords.txt", "w") as f:
    #         f.write(f"{origin_coords[0]},{origin_coords[1]}")
    # else:
    #     print("No se pudieron obtener las coordenadas de origen.")

    # Obtener coordenadas de los municipios
    municipios_coords_data = []
    try:
        with open("municipios_malaga.txt", "r", encoding="utf-8") as f_mun:
            municipios = [line.strip() for line in f_mun if line.strip()]
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'municipios_malaga.txt'")
        exit()

    print(f"Procesando {len(municipios)} municipios...")

    with open("municipios_coords.csv", "w", encoding="utf-8") as f_out:
        f_out.write("Municipio,Latitud,Longitud\n") # Encabezado CSV
        for i, municipio_nombre in enumerate(municipios):
            address_to_geocode = f"{municipio_nombre}, Málaga, Spain"
            coords = get_coords(address_to_geocode)
            if coords:
                print(f"[{i+1}/{len(municipios)}] Coordenadas para {municipio_nombre}: {coords}")
                f_out.write(f"{municipio_nombre},{coords[0]},{coords[1]}\n")
            else:
                print(f"[{i+1}/{len(municipios)}] No se pudieron obtener coordenadas para {municipio_nombre}. Se escribirá None.")
                f_out.write(f"{municipio_nombre},None,None\n")
            
            # Pausa para no sobrecargar el API de Nominatim
            time.sleep(1) # Esperar 1 segundo entre peticiones

    print("Coordenadas de municipios guardadas en 'municipios_coords.csv'")

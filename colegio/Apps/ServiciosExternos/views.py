from django.shortcuts import render
import requests
from django.http import JsonResponse
from .models import AccesosExternos


def IndexJustificaciones(request):
    return render(request,'justificaciones/index_justificaciones.html')

def ListarJustificaciones(request):
    try:
        acceso = AccesosExternos.objects.first()
        if not acceso:
            return JsonResponse({"error": "No se encontró la configuración de acceso a la API"}, status=400)

        url_api = acceso.url
        token_api = acceso.token

        # Obtener los filtros desde la URL
        grado = request.GET.get("gradoFilter", "").strip()
        seccion = request.GET.get("seccionFilter", "").strip()

        # Construir los parámetros sin valores vacíos
        params = {k: v for k, v in {"gradoFilter": grado, "seccionFilter": seccion}.items() if v}

        headers = {
            "Authorization": f"Token {token_api}",
            "Content-Type": "application/json"
        }

        # Hacer la petición GET con los filtros
        response = requests.get(url_api, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            logger.error(f"Error en la API {url_api}: {response.status_code} - {response.text}")
            return JsonResponse({"error": "No se pudo obtener las justificaciones", "detalle": response.text}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión: {str(e)}")
        return JsonResponse({"error": "No se pudo conectar con la API externa", "detalle": str(e)}, status=500)
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return JsonResponse({"error": "Error interno del servidor", "detalle": str(e)}, status=500)
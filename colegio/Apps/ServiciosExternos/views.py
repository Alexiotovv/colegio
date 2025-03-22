from django.shortcuts import render
import requests
from django.http import JsonResponse
from .models import AccesosExternos


def IndexJustificaciones(request):
    return render(request,'justificaciones/index_justificaciones.html')

def ListarJustificaciones(request):
    acceso = AccesosExternos.objects.first()
    if acceso:
        url_api = acceso.url
        token_api = acceso.token
    else:
        return JsonResponse({"error": "No se encontró la configuración de acceso a la API"}, status=400)

    # Obtener los filtros desde la URL
    grado = request.GET.get("gradoFilter", "")
    seccion = request.GET.get("seccionFilter", "")

    # Construir la URL con los parámetros de filtro
    params = {}
    if grado:
        params["gradoFilter"] = grado
    if seccion:
        params["seccionFilter"] = seccion

    headers = {
        "Authorization": f"Token {token_api}",
        "Content-Type": "application/json"
    }

    # Hacer la petición GET con los filtros
    response = requests.get(url_api, headers=headers, params=params)

    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "No se pudo obtener las justificaciones"}, status=response.status_code)
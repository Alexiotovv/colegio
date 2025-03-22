from django.shortcuts import render
import requests
from django.http import JsonResponse

def ListarJustificaciones(request):
    url = "http://localhost:8000/api/v1/list/justificaciones/"  # Reemplaza con la URL real de tu API
    token = "a8cc3f66eab1c536204a1abcbe60e40eacac59cd"  # Reemplaza con el token de autenticación

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return JsonResponse({"error": "No se pudo obtener las justificaciones"}, status=response.status_code)
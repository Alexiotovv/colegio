from django.shortcuts import render
from colegio.Apps.Pagos.models import Pagos
from django.http import JsonResponse

def RegistrarPago(request):
    
    existe=Pagos.objects.filter(Dni=request.POST.get("Dni"),PagoMes=request.POST.get("pago_mes"),PagoAno=request.POST.get("pago_ano")).exists()
    
    if existe:
        data={'mensaje':existe}
    else:
        obj=Pagos()
        obj.Dni=request.POST.get("Dni")
        obj.PagoMes=request.POST.get("pago_mes")
        obj.PagoAno=request.POST.get("pago_ano")
        obj.save()
        data={'mensaje':existe}
    return JsonResponse(data)
    

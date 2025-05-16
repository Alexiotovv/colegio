from django.shortcuts import render
from colegio.Apps.Pagos.models import Pagos
from django.http import JsonResponse
from colegio.Apps.Apis.models import Venta
from django.db.models import Q
from django.core.paginator import Paginator

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
    
def ListarPagos(request):
    query = request.GET.get('q', '')
    # ventas = Venta.objects.all()
    ventas = Venta.objects.order_by('descripcion', 'Concepto', 'Mes').distinct('descripcion', 'Concepto', 'Mes')

    if query:
        ventas = ventas.filter(
            Q(NombreCompleto__icontains=query) |
            Q(Dni__icontains=query)
        )

    paginator = Paginator(ventas.order_by('-FechaPago'), 15)  # 10 resultados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request,"pagos/pagos.html",context)
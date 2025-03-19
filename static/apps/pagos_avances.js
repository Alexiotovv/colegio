$("#btnPagar").on("click",function (e) {
    e.preventDefault();
    var serializedData=$("#formPagar").serialize();
    dni=$("#Dni").val();	
    pago_mes=$("#pago_mes").val();
    if (dni=='--' || pago_mes=='--') {
        alert("Seleccione un mes dni o mes de pago");
    }else{
        $.ajax({
            type: "POST",
            url: "/pagos/registrar_pago/",
            data: serializedData,
            dataType: "json",
            success: function (response) {
                if (response.mensaje) {
                    round_warning_noti("El Pago de este DNi ya se ha Registrado")
                }else{
                    round_success_noti("Pago Registrado Correctamente")
                }
            }
        });
    }
})
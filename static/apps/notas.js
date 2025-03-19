
$(Document).on("click",".btnFiltrar",function (e) {
    e.preventDefault();
    anhio=$("#AnoAcademico").val();
    $("#DTMatriculados tbody").html("");
    $.ajax({
        type: "GET",
        url: "MatriculasPorAno/" + anhio,
        dataType: "json",
        success: function (response) {       
            $("#DTMatriculados").DataTable({
                "destroy":true,
                "data":response,
                "method":"GET",
                "columns":[
                    {data:"id"},
                    {data:"Alumno__DNI"},
                    {"render":
                        function ( data, type, row ) {
                            return (row["Alumno__ApellidoPaterno"]+ ' ' + row["Alumno__ApellidoMaterno"]+', '+row["Alumno__Nombres"]);
                        }
                    },
                    {data:"Grado"},
                    {data:"Seccion"},
                    {"defaultContent":
                    "<button type='submit' class='btn-info btn-sm btnIBimestre'>IBIM</button>\
                    <button type='submit' class='btn-success btn-sm btnIIBimestre'>IIBIM</button>\
                    <button type='submit' class='btn-warning btn-sm btnIIIBimestre'>IIIBIM</button>\
                    <button type='submit' class='btn-danger btn-sm btnIVBimestre'>IVBIM</button>"}
                    ,
                ],
                "buttons": [ 'copy', 'excel', 'pdf', 'print'],
                dom: 'Bfrtip',
                // order:[0],
            }); 
        }
    });
   
});

$(Document).on("click",".btnIBimestre",function(e){
    // e.preventDefault();
    fila=$(this).closest("tr");
    $("#Grado").val((fila).find('td:eq(3)').text());
    $("#Seccion").val((fila).find('td:eq(4)').text());
    $("#Pacademico").val(1);//el numero 1 es el id del bimestre
    $("#idMat").val((fila).find('td:eq(0)').text());
});

$(Document).on("click",".btnIIBimestre",function(e){
    // e.preventDefault();
    fila=$(this).closest("tr");
    $("#Grado").val((fila).find('td:eq(3)').text());
    $("#Seccion").val((fila).find('td:eq(4)').text());
    $("#Pacademico").val(2);//el numero 1 es el id del bimestre
    $("#idMat").val((fila).find('td:eq(0)').text());
});

$(Document).on("click",".btnIIIBimestre",function(e){
    // e.preventDefault();
    fila=$(this).closest("tr");
    $("#Grado").val((fila).find('td:eq(3)').text());
    $("#Seccion").val((fila).find('td:eq(4)').text());
    $("#Pacademico").val(4);//el numero 1 es el id del bimestre
    $("#idMat").val((fila).find('td:eq(0)').text());
});

$(Document).on("click",".btnIVBimestre",function(e){
    // e.preventDefault();
    fila=$(this).closest("tr");
    $("#Grado").val((fila).find('td:eq(3)').text());
    $("#Seccion").val((fila).find('td:eq(4)').text());
    $("#Pacademico").val(5);//el numero 1 es el id del bimestre
    $("#idMat").val((fila).find('td:eq(0)').text());
});



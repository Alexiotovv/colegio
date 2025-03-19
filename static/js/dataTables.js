$(document).ready(function() {
    // Setup - add a text input to each footer cell
    $('#example thead tr').clone(true).appendTo( '#example thead' );
    $('#example thead tr:eq(1) th').each( function (i) {
        var title = $(this).text();
        $(this).html( '<input type="text" class="form-control" placeholder="Buscar '+title+'" />' );
 
        $( 'input', this ).on( 'keyup change', function () {
            if ( table.column(i).search() !== this.value ) {
                table
                    .column(i)
                    .search( this.value )
                    .draw();
            }
        } );
    } );


    var table = $('#example').DataTable({

        dom: 'Bfrtip',
        buttons: [{
            extend: 'excelHtml5',
            customize: function(xlsx) 
            {
                var sheet = xlsx.xl.worksheets['sheet1.xml'];
 
                // Loop over the cells in column `C`
                $('row c[r^="C"]', sheet).each( function () 
                {
                    // Get the value
                    if ( $('is t', this).text() == 'New York' )
                    {
                        $(this).attr( 's', '20' );
                    }

                });
            }
        }]
        ,orderCellsTop: true,
        fixedHeader: true
    });

        


} );


def handle_uploaded_file(f):  
    with open('/var/www/vhosts/colegio_venv_37/colegio/media/upload/'+f.name,'wb+') as destination:
    	for chunk in f.chunks():
    		destination.write(chunk) 
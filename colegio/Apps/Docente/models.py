from django.db import models
from django.contrib.auth.models import User

class Docente (models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    GradoNivel=models.CharField(max_length=60,default='-')
    Seccion=models.CharField(max_length=20,default='-')
    DNI = models.CharField(max_length=8)
    Direccion = models.CharField(max_length=100,default='')
    FechaNacimiento = models.DateField()
    SEXOS =  (('M','Masculino'),('F','Femenino'))
    Sexo = models.CharField(max_length=1,choices=SEXOS,default='M')
    Telefono = models.CharField(max_length=60)
    TUTOR_GRADOS=(('-','-'),('1PRIM','1PRIM'),('2PRIM','2PRIM'),('3PRIM','3PRIM'),('4PRIM','4PRIM'),('5PRIM','5PRIM'),('6PRIM','6PRIM'),('1SEC','1SEC'),('2SEC','2SEC'),('3SEC','3SEC'),('4SEC','4SEC'),('5SEC','5SEC'))
    TutorGrado=models.CharField(max_length=10,choices=TUTOR_GRADOS,default='-')
    TUTOR_SECCIONES=(('-','-'),('A','A'),('B','B'),('C','C'),('D','D'),('E','E'),('F','F'),('G','G'))
    TutorSeccion=models.CharField(max_length=10,choices=TUTOR_SECCIONES,default='-')
    def NombreCompleto(self):
        cadena = "{0} {1}"
        return cadena.format(self.User.first_name,self.User.last_name)

    def __str__ (self):
        return self.NombreCompleto()

import numpy as np
import matplotlib.pyplot as plt
import math as m
import os


#Extraemos los datos de posicion1.csv en forma de vectores, si no existe el fichero avisará y terminará la ejecución.
ruta='./datos/posicion1.csv'

if not os.path.exists(ruta):
    print('No existe el fichero con los datos, ejecuta rk4_orbita.py')
    exit()

file=open(ruta,'r')
lineas=file.readlines()
separado=[(x.replace('\n','')).split(',') for x in lineas]
list_v1=[np.array([float(x[0])]+[float(x[1])]) for x in separado]

#Saco la matriz de giro de tal manera que la posición de la tierra en el solsticio de verano no tenga componente Y.
ang_rot=-m.atan(list_v1[0][1]/list_v1[0][0])
Matriz_giro_2D=np.array([[np.cos(ang_rot),-np.sin(ang_rot)],[np.sin(ang_rot),np.cos(ang_rot)]])

#Aplico el giro a todos los puntos.
orbit=[np.dot(Matriz_giro_2D,x) for x in list_v1]

#Cambio el origen a la Tierra, ahora tendremos las coordenadas del Sol.
orbit_centro_tierra=[-x for x in orbit]


def coords(list):
    m=len(list)
    n=len(list[0])
    sol=[]
    for i in range(0,n):
        sol.append([x[i] for x in list])
    return sol

#Le añado componente z=0 a cada punto.
orbit_mas_z=[np.concatenate((x,np.array(0)),axis=None) for x in orbit_centro_tierra]

#Creamos la matriz de giro de tal manera que el eje de rotación sea el eje z, para ello definimos la matriz de giro apropiada usando la oblicuidad de la eclíptica.
oblicuidad=(23.44*2*np.pi)/360
Matriz_giro_3D=np.array([[np.cos(oblicuidad),0,np.sin(oblicuidad)],[0,1,0],[-np.sin(oblicuidad),0,np.cos(oblicuidad)]])

#Aplicamos el giro.
orbit_3D=[np.dot(Matriz_giro_3D,x) for x in orbit_mas_z]

#Normalizamos los vectores posición para colocarlos sobre la esfera unidad (Esfera Celeste).
orbit_3D_norm=[x/np.linalg.norm(x) for x in orbit_3D]

#Ahora añadiremos el efecto de rotación terreste. Para ello asignaremos un instante de tiempo(s) a cada punto.
particiones=len(orbit_3D_norm)
parT=np.linspace(0,365*24*3600,particiones)

#Definimos el periodo de rotación terreste(s).
T=23*3600+56*60+4

#Asumiendo velocidad angular constante, asigno a cada punto un ángulo.
angulos=[]
for i in range (0,particiones):
    a= -2*np.pi*parT[i]/T
    angulos.append(a)

#Creo un bucle, en el cual a cada punto se le aplicará un giro correspondiente al angulo asignado anteriormente, a causa de la rotación.
orbit_final=[]
for i in range (0,particiones):
    ang=angulos[i]
    M_giro=[[np.cos(ang),-np.sin(ang),0],[np.sin(ang),np.cos(ang),0],[0,0,1]]
    p=orbit_3D_norm[i]
    orbit_final.append(np.dot(M_giro,p))



#Guardamos los datos obtenidos en un archivo llamado: posicionFinal.csv
text2save=[str(x[0])+','+str(x[1])+','+str(x[2]) for x in orbit_final]

ruta='./datos/posicionFinal.csv'

if not os.path.exists("./datos"):
    os.makedirs('datos')

file=open(ruta,'w')
file.writelines('\n'.join(text2save))
file.close()






#coordenadas=(coords(orbit_final))

#ax = plt.axes(projection='3d')
#ax.set_aspect("equal")
#ax.set_xlim(-1.25,1.25)
#ax.set_ylim(-1.25,1.25)
#ax.set_zlim(-1.25,1.25)
#ax.set_box_aspect((1, 1, 1)) 
#ax.plot_surface((np.sqrt(1-Z**2))*np.cos(A),(np.sqrt(1-Z**2))*np.sin(A),Z,alpha=0.2)
#ax.plot3D(coordenadas[0], coordenadas[1], coordenadas[2], '-k',label="Órbita del Sol")
#ax.plot3D(0, 0, 0, 'ob',label="Tierra")
#ax.plot3D(coordenadas[0][0],coordenadas[1][0],coordenadas[2][0],'oy',label="Solsticio de Verano")

#plt.show()
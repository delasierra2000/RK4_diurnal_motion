import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, PillowWriter
import math as m
import os
from time import time
from datetime import datetime


#Defino las funciones que usaré.
def coords(list):
    n=len(list[0])
    sol=[]
    for i in range(0,n):
        sol.append([x[i] for x in list])
    return sol

def vect(list):
    m=len(list[0])
    n=len(list)
    sol=[]
    for j in range(0,m):
        l=[]
        for i in range(0,n):
            l.append(list[i][j])
        sol.append(np.array(l))
    return sol


#Extraigo los datos de posicionFinal.csv en forma de vectores, si no existe el fichero avisará y terminará la ejecución.
ruta='./datos/posicionFinal.csv'

if not os.path.exists(ruta):
    print('\nNo existe el fichero con los datos, ejecuta calc_mov_diurno.py\n')
    exit()


file=open(ruta,'r')
lineas=file.readlines()
separado=[(x.replace('\n','')).split(',') for x in lineas]
orbit_final=[np.array([float(x[0])]+[float(x[1])]+[float(x[2])]) for x in separado]

#Creo un lista que contiene 3 listas, una para cada componente.
coordenadas=coords(orbit_final)

#Establezco los segundos que queremos que dure la animación y los frames por segundo:
s=30
fps=30

#Añado la ruta de ffmpeg.exe, le ponemos nombre y creador al video, y establecemos los fps.
plt.rcParams['animation.ffmpeg_path'] = 'D:\\Fran\\python\\Astronomía\\ffmpeg-2024-11-28-git-bc991ca048-full_build\\bin\\ffmpeg.exe'
metadata=dict(tittle='Movie',artist='Fran')
writer=FFMpegWriter(fps=30,metadata=metadata)

#De las posiciones, me quedo con indices equitativamente distribuidos, de tal manera que tengamos tantos indices como frames totales.
indices=[m.trunc(x) for x in np.linspace(0,len(coordenadas[1][:11520])-1,fps*s)]

#Creo la variable longitud para saber cuantas veces hay que repetir el bucle y añadirlo al contador.
longitud=len(indices)


#Creo la figura.
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

#Saco la fecha correspondiente a cada instante, empezando el 21 de Junio.
dt = datetime(2023, 6, 21, 0, 0)-datetime(1970,1,1)
start_time=dt.total_seconds()
l_time=np.linspace(0,365*24*3600,len(coordenadas[1]))
l_time_actual=[x+start_time for x in l_time]
l_texto=[datetime.fromtimestamp(x).strftime("%B %d, %Y") for x in l_time_actual]

#Defino el título y todas las modificaciones a la figura (limite de los ejes, escala, etiquetas...)
plt.title("Orto y Ocaso\ndel Sol",bbox=dict(facecolor='none', edgecolor='k', pad=5.0),size='x-large')

ax.set_xlim(-1.25,1.25)
ax.set_ylim(-1.25,1.25)
ax.set_zlim(-1.25,1.25)
ax.set_box_aspect((1, 1, 1)) 

ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

ax.view_init(8,45,0)

#Represento la esfera unidad (Esfera celeste).
arg=np.arange(0,2*np.pi,0.001)
z=np.arange(-1,1,0.001)
A,Z=np.meshgrid(arg,z)
ax.plot_surface((np.sqrt(1-Z**2))*np.cos(A),(np.sqrt(1-Z**2))*np.sin(A),Z,alpha=0.2,color='#a5f4f3')

#Represento el vector correspondiente al Polo.
ax.quiver(0,0,-1.5,0,0,3,color='k',arrow_length_ratio=0.07)

#Represento el ecuador, para ello parametrizo.
theta=np.linspace(0,2*np.pi,10000)

x0=[np.cos(x) for x in theta]
y0=[np.sin(x) for x in theta]
z0=[0 for x in x0]
ax.plot3D(x0,y0,z0,'-b',alpha=0.2)


#Represento el plano del horizonte, para ello introduzco lambda y phi, y aplico los giros necesarios a la circunferencia del ecuador.
lamda=np.pi/2+np.pi/5
Rot_z=np.array([[np.cos(lamda),-np.sin(lamda),0],[np.sin(lamda),np.cos(lamda),0],[0,0,1]])

phi_rot=np.pi/4
phi=np.pi/2-phi_rot
Rot_y=np.array([[np.cos(phi),0,np.sin(phi)],[0,1,0],[-np.sin(phi),0,np.cos(phi)]])

listas_puntos=vect([x0,y0,z0])

puntos_rotados=[np.dot(Rot_z,np.dot(Rot_y,x)) for x in listas_puntos]

posicion_horizonte=coords(puntos_rotados)

ax.plot3D(posicion_horizonte[0],posicion_horizonte[1],posicion_horizonte[2],'-',color='#1331ee',alpha=0.4)

#Represento también el vector correspondiente al Zénit.
punto=np.dot(Rot_z,np.dot(Rot_y,np.array([0,0,1.5])))

ax.quiver(-punto[0],-punto[1],-punto[2],2*punto[0],2*punto[1],2*punto[2],color='k',arrow_length_ratio=0.07)

#Calculo los puntos correspondientes al orto y al ocaso y lo represento.
r=np.cos((23.44*2*np.pi)/360)
z_c=np.sqrt(1-r**2)


tita1=m.acos(-z_c/np.sin(phi))
tita2=-m.acos(-z_c/np.sin(phi))+2*np.pi


temporal_p=np.array([np.cos(tita1),np.sin(tita1),0])
punto1=np.dot(Rot_z,np.dot(Rot_y,temporal_p))
ax.plot3D(punto1[0],punto1[1],punto1[2],'ok')

temporal_p=np.array([np.cos(tita2),np.sin(tita2),0])
punto2=np.dot(Rot_z,np.dot(Rot_y,temporal_p))
ax.plot3D(punto2[0],punto2[1],punto2[2],'ok')

#Calculo la componente angular en coordenadas cilíndricas de orto y el ocaso, para trazar el recorrido del día y la noche.
punto_origen=np.array([0,0,z_c])
punto_ref=np.array([r,0,z_c])


a1=np.linalg.norm(punto_origen-punto_ref)
b1=np.linalg.norm(punto_origen-punto1)
c1=np.linalg.norm(punto1-punto_ref)
angle1=-m.acos((c1**2-a1**2-b1**2)/(-2*a1*b1))+2*np.pi



a2=np.linalg.norm(punto_origen-punto_ref)
b2=np.linalg.norm(punto_origen-punto2)
c2=np.linalg.norm(punto2-punto_ref)
angle2=m.acos((c2**2-a2**2-b2**2)/(-2*a2*b2))

#Represento los dos tramos de circunferiencia, cada tramo es correspondiente al dia o a la noche.
tramo1_theta=np.linspace(angle2,angle1,1000)
tramo2_theta=np.linspace(-(2*np.pi-angle1),angle2,1000)
x1=[r*np.cos(x) for x in tramo1_theta]
y1=[r*np.sin(x) for x in tramo1_theta]
z=[z_c for x in y1]
x2=[r*np.cos(x) for x in tramo2_theta]
y2=[r*np.sin(x) for x in tramo2_theta]

ax.plot3D(x1,y1,z,'-',color='#ee13da',alpha=0.4)
ax.plot3D(x2,y2,z,'-',color='#478712',alpha=0.4)


#Represento el origen.
ax.plot3D(0,0,0,'ok')


#Añado texto para indicar los nombres de los vectores, y el ecuador.
ax.text(-0.15, 0.05, 1.15, "P", color='k',size='xx-large')
ax.text(-1.6, 0.05, 0.7, "Z", color='k',size='xx-large')
ax.text(-0.75, 0.75, 0, " Ecuador", color='k',size='x-small')

#Inicio el proceso de animación.
#Crearé un bucle, en cada bucle se actualizará la gráfica y se guardará.
x=coordenadas[0]
y=coordenadas[1]
z=coordenadas[2]

#Añado un contador de tiempo
start = time()
with writer.saving(fig,"./animaciones/orto_ocaso.mp4",250):
    #Creo un bucle en el que en cada ciclo se actualiza la fecha y la posición del sol.
    temporary=ax.text(0, 0, 1.75, 'prueba', color='k',size='medium', bbox=dict(facecolor='none', edgecolor='k', pad=5.0),ha='center')
    for i in indices:
        print(str(indices.index(i)+1)+'/'+str(longitud))
        temp,=ax.plot3D(x[i],y[i],z[i],'o',color='#fbb506')
        temporary.set_text(l_texto[i])
        writer.grab_frame()
        temp.remove()

#Saco por la ventana el tiempo de ejecución.
print(time() - start)





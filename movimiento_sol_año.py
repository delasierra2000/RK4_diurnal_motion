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

#Extraemos los datos de posicionFinal.csv en forma de vectores, si no existe el fichero avisará y terminará la ejecución.
ruta='./datos/posicionFinal.csv'

if not os.path.exists(ruta):
    print('No existe el fichero con los datos, ejecuta calc_mov_diurno.py')
    exit()

file=open(ruta,'r')
lineas=file.readlines()
separado=[(x.replace('\n','')).split(',') for x in lineas]
orbit_final=[np.array([float(x[0])]+[float(x[1])]+[float(x[2])]) for x in separado]

#Creo un lista que contiene 3 listas, una para cada componente.
coordenadas=coords(orbit_final)

#Establezco los segundos que queremos que dure la animación y los frames por segundo:
s=365
fps=30

#Añado la ruta de ffmpeg.exe, le ponemos nombre y creador al video, y establecemos los fps.
plt.rcParams['animation.ffmpeg_path'] = 'D:\\Fran\\python\\Astronomía\\ffmpeg-2024-11-28-git-bc991ca048-full_build\\bin\\ffmpeg.exe'
metadata=dict(tittle='Movie',artist='Fran')
writer=FFMpegWriter(fps=30,metadata=metadata)

#De las posiciones, me quedo con indices equitativamente distribuidos, de tal manera que tengamos tantos indices como frames totales.
indices=[m.trunc(x) for x in np.linspace(0,len(coordenadas[1])-1,fps*s)]

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
plt.title("Movimiento diurno\na lo largo de un año",bbox=dict(facecolor='none', edgecolor='k', pad=5.0),size='x-large')

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

#Represento el ecuador y los trópicos, para ello parametrizo.
r=np.cos((23.44*2*np.pi)/360)
theta=np.linspace(0,2*np.pi,10000)
x1=[r*np.cos(x) for x in theta]
y1=[r*np.sin(x) for x in theta]
z_c=np.sqrt(1-r**2)
z1=[z_c for x in y1]

x2=[-x for x in x1]
y2=[-x for x in y1]
z2=[-x for x in z1]

x0=[np.cos(x) for x in theta]
y0=[np.sin(x) for x in theta]
z0=[0 for x in x0]

ax.plot3D(x1,y1,z1,'-b',alpha=0.2)
ax.plot3D(x2,y2,z2,'-b',alpha=0.2)
ax.plot3D(x0,y0,z0,'-b',alpha=0.2)

#Añado texto para indicar los nombres de los vectores, y el ecuador.
ax.text(-0.15, 0.05, 1.15, "P", color='k',size='xx-large')
ax.text(-0.65, 0.65, z_c+0.15, "  Trópico \nde Cáncer", color='k',size='x-small')
ax.text(-0.6, 0.6, -z_c-0.27, "      Trópico \nde Capricornio", color='k',size='x-small')
ax.text(-0.75, 0.75, 0, " Ecuador", color='k',size='x-small')

#Represento el origen.
ax.plot3D(0,0,0,'ok')

#Inicio el proceso de animación.
#Crearé un bucle, en cada bucle se actualizará la gráfica y se guardará.
x=coordenadas[0]
y=coordenadas[1]
z=coordenadas[2]

#Añado un contador de tiempo
start = time()

#Si no existe la carpeta animaciones, la crea.
if not os.path.exists("./animaciones"):
    os.makedirs('animaciones')
    
with writer.saving(fig,"./animaciones/año_movimiento_sol.mp4",250):
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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, PillowWriter
import math as m
import os
from time import time
from datetime import datetime

#----------------------------------------------------------
#Parameters:

#Date format: 'MM-DD'
date='10-14'

#Parameters of Zenith on degrees.
phi_zenith=45
lamda_zenith=115

#If automatic_lamda is True, the program will calculate the value of lamda_zenith depending on the value of phi_zenith for better visualization.
#Change it to False if you want to set the value of lamda_zenith manually.
automatic_lambda=True

#----------------------------------------------------------



#Defino las funciones que usaré.
def año_decimal(str):
    año=float(str[0:4])
    mes=float(str[5:7])
    dia=float(str[8:10])

    if año%400:
        b=29
    elif año%100:
        b=28
    elif año%4:
        b=29
    else:
        b=28

    duracion_meses=[31,b,31,30,31,30,31,31,30,31,30,31]

    if mes>=2:
        dp=sum(duracion_meses[0:int(mes-1)])
    else:
        dp=0
    
    año_dec=año+(dp+dia-1)/(sum(duracion_meses))
    return  año_dec

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


month=int(date[0:2])
day=int(date[3:5])

if (month==6 and day>=21) or month>6:
    year=str(2023)
else:
    year=str(2024)

f_date=año_decimal(year+'-'+date)

fraction_time=(f_date-año_decimal('2023-06-21'))
indice2=int(round(len(coordenadas[0])*fraction_time))


indices=[m.trunc(x) for x in np.linspace(0+indice2,11520-1+indice2,fps*s)]

#Creo la variable longitud para saber cuantas veces hay que repetir el bucle y añadirlo al contador.
longitud=len(indices)


#Creo la figura.
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))


#Defino el título y todas las modificaciones a la figura (limite de los ejes, escala, etiquetas...)
plt.title("Raising and Setting\nof the Sun",bbox=dict(facecolor='none', edgecolor='k', pad=5.0),size='x-large')

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


if automatic_lambda:
    lamda_zenith=45+90-20
    if phi_zenith<=-8:
        lamda_zenith=45+90+20

lamda=(lamda_zenith*2*np.pi)/360
Rot_z=np.array([[np.cos(lamda),-np.sin(lamda),0],[np.sin(lamda),np.cos(lamda),0],[0,0,1]])

phi=90-phi_zenith
phi_f=(phi*2*np.pi)/360
Rot_y=np.array([[np.cos(phi_f),0,np.sin(phi_f)],[0,1,0],[-np.sin(phi_f),0,np.cos(phi_f)]])

listas_puntos=vect([x0,y0,z0])

puntos_rotados=[np.dot(Rot_z,np.dot(Rot_y,x)) for x in listas_puntos]

posicion_horizonte=coords(puntos_rotados)

ax.plot3D(posicion_horizonte[0],posicion_horizonte[1],posicion_horizonte[2],'-',color='r',alpha=0.4)

#Represento también el vector correspondiente al Zénit.
punto=np.dot(Rot_z,np.dot(Rot_y,np.array([0,0,1.5])))

ax.quiver(-punto[0],-punto[1],-punto[2],2*punto[0],2*punto[1],2*punto[2],color='k',arrow_length_ratio=0.07)

#Calculo los puntos correspondientes al orto y al ocaso y lo represento.

#Date format: 'MM-DD'


print(indice2)
ind_sol_x=coordenadas[0][indice2]
ind_sol_y=coordenadas[1][indice2]
ind_sol_z=coordenadas[2][indice2]

r=np.sqrt(ind_sol_x**2+ind_sol_y**2)
z_c=ind_sol_z

l_tita=np.linspace(lamda+np.pi,lamda+3*np.pi,10000)
sol_x=[r*np.cos(x) for x in l_tita]
sol_y=[r*np.sin(x) for x in l_tita]
sol_z=[z_c for x in sol_y]


sol_vectP=vect([sol_x ,sol_y ,sol_z])

dia=[x for x in sol_vectP if punto[0]*x[0]+punto[1]*x[1]+punto[2]*x[2]>0]
noche=[x for x in sol_vectP if punto[0]*x[0]+punto[1]*x[1]+punto[2]*x[2]<=0]

if dia:
    coords_dia=coords(dia)
    ax.plot3D(coords_dia[0],coords_dia[1],coords_dia[2],'-',color='#3a7707',alpha=0.6)
if noche:
    i_salto=int(round(len(noche)/2))
    noche=noche[i_salto+10:]+noche[:i_salto-10]
    coords_noche=coords(noche)
    ax.plot3D(coords_noche[0],coords_noche[1],coords_noche[2],'-',color='#0000ff',alpha=0.6)
if dia and noche:
    orto=dia[1]
    ocaso=dia[-1]
    ax.plot3D(orto[0],orto[1],orto[2],'o',color='k')
    ax.plot3D(ocaso[0],ocaso[1],ocaso[2], 'o',color='k')

    t=np.linspace(0,1,1000)
    x_segment=[]
    y_segment=[]
    z_segment=[]
    for i in range(0,len(t)):
        x_segment.append(orto[0]+t[i]*(ocaso[0]-orto[0]))
        y_segment.append(orto[1]+t[i]*(ocaso[1]-orto[1]))
        z_segment.append(orto[2]+t[i]*(ocaso[2]-orto[2]))
    ax.plot3D(x_segment,y_segment,z_segment,'--',color='k',alpha=0.4)

#Represento el origen.
ax.plot3D(0,0,0,'ok')

#Añado texto para indicar los nombres de los vectores, y el ecuador.
ax.text(-0.15, 0.05, 1.15, "P", color='k',size='xx-large')
ax.text(punto[0], punto[1]+0.2, punto[2], "Z", color='k',size='xx-large')
ax.text(-0.75, 0.75, 0, " Ecuador", color='k',size='x-small')
ax.text(0, 0, 1.75, datetime.strptime(date, '%m-%d').strftime("%B %d"), color='k',size='medium', bbox=dict(facecolor='none', edgecolor='k', pad=5.0),ha='center')

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

with writer.saving(fig,"./animaciones/orto_ocaso.mp4",250):
    #Creo un bucle en el que en cada ciclo se actualiza la fecha y la posición del sol.
    for i in indices[:30]:
        print(str(indices.index(i)+1)+'/'+str(longitud))
        temp,=ax.plot3D(x[i],y[i],z[i],'o',color='#fbb506')
        writer.grab_frame()
        temp.remove()

#Saco por la ventana el tiempo de ejecución.
print(time() - start)
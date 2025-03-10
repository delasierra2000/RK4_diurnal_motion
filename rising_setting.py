import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import math as m
import os
from time import time
from datetime import datetime

#----------------------------------------------------------
#Parameters:

#Date format: 'MM-DD'
date='03-20'

#Parameters of Zenith on degrees.
phi_zenith=36
λ_zenith=115

#If automatic_λ is True, the program will calculate the value of λ_zenith depending on the value of phi_zenith for better visualization.
#Change it to False if you want to set the value of λ_zenith manually.
automatic_λ=True

#(WINDOWS) Root of the path where ffmpeg.exe is located.
#(LINUX) Root of the path where ffmpeg is located. You can find it by typing 'which ffmpeg' in the terminal.
ffmpeg_root='C:\\Users\\Astronomia\\Desktop\\Fran\\Programacion\\Herramientas\\ffmpeg-7.1-essentials_build\\bin\\ffmpeg.exe'

#Duration of the video in seconds and frames per second.
s=30
fps=30

#----------------------------------------------------------

#Auxiliary functions:
def dec_year(str):
    year=float(str[0:4])
    month=float(str[5:7])
    day=float(str[8:10])

    if year%400:
        b=29
    elif year%100:
        b=28
    elif year%4:
        b=29
    else:
        b=28

    duration_month=[31,b,31,30,31,30,31,31,30,31,30,31]

    if month>=2:
        dp=sum(duration_month[0:int(month-1)])
    else:
        dp=0
    
    year_dec=year+(dp+day-1)/(sum(duration_month))
    return  year_dec

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


#Extract the data from posicionFinal.csv in the form of vectors, if the file does not exist it will warn and end the execution.
ruta='./datos/posicionFinal.csv'

if not os.path.exists(ruta):
    print('\nNo existe el fichero con los datos, ejecuta calc_mov_diurno.py\n')
    exit()


file=open(ruta,'r')
lines=file.readlines()
splitted=[(x.replace('\n','')).split(',') for x in lines]
orbit_final=[np.array([float(x[0])]+[float(x[1])]+[float(x[2])]) for x in splitted]

#Create a list that contains 3 lists, one for each component.
orbit_coords=coords(orbit_final)
x_orbit=orbit_coords[0]
y_orbit=orbit_coords[1]
z_orbit=orbit_coords[2]

#Add the path of ffmpeg.exe, set the title and artist of the video, and set the fps.
plt.rcParams['animation.ffmpeg_path'] = ffmpeg_root
metadata=dict(tittle='Movie',artist='Fran')
writer=FFMpegWriter(fps=30,metadata=metadata)

#The data starts at 2023-06-21, so I will calculate the fraction of time that has passed since then, and I will use it to calculate the position of the sun.
month=int(date[0:2])
day=int(date[3:5])

if (month==6 and day>=21) or month>6:
    year=str(2023)
else:
    year=str(2024)

f_date=dec_year(year+'-'+date)

fraction_time=(f_date-dec_year('2023-06-21'))
index_sun0=int(round(len(x_orbit)*fraction_time))

#Create a list with the indexes of the positions of the sun that will be represented according with the fps and the duration of the video.
indexes=[m.trunc(x) for x in np.linspace(0+index_sun0,11520-1+index_sun0,fps*s)]

#Create the variable frames to know how many times the loop has to be repeated and show it on the terminal.
frames=len(indexes)

#Create the figure.
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

#Define the title and all the modifications to the figure (axes limits, scale, labels...)
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

#Calculation and representation of the unit sphere (Celestial sphere).
arg=np.arange(0,2*np.pi,0.001)
z=np.arange(-1,1,0.001)
A,Z=np.meshgrid(arg,z)
ax.plot_surface((np.sqrt(1-Z**2))*np.cos(A),(np.sqrt(1-Z**2))*np.sin(A),Z,alpha=0.2,color='#a5f4f3')

#Representation of the vector corresponding to the Pole.
ax.quiver(0,0,-1.5,0,0,3,color='k',arrow_length_ratio=0.07)

#Represantion of the equator, for that I will parametrize it.
theta=np.linspace(0,2*np.pi,10000)

ecuator_x=[np.cos(x) for x in theta]
ecuator_y=[np.sin(x) for x in theta]
ecuator_z=[0 for x in ecuator_x]
ax.plot3D(ecuator_x,ecuator_y,ecuator_z,'-b',alpha=0.4)


#Representation of the horizon plane, for that I will introduce λ and φ, and apply the necessary rotations to the equator circumference.
if automatic_λ:
    λ_zenith=45+90-20
    if phi_zenith<=-8:
        λ_zenith=45+90+20

λ=(λ_zenith*2*np.pi)/360
Rot_z=np.array([[np.cos(λ),-np.sin(λ),0],[np.sin(λ),np.cos(λ),0],[0,0,1]])

phi=90-phi_zenith
phi_f=(phi*2*np.pi)/360
Rot_y=np.array([[np.cos(phi_f),0,np.sin(phi_f)],[0,1,0],[-np.sin(phi_f),0,np.cos(phi_f)]])

sample_circ=vect([ecuator_x,ecuator_y,ecuator_z])

rotated_circ=[np.dot(Rot_z,np.dot(Rot_y,x)) for x in sample_circ]

horizon=coords(rotated_circ)

ax.plot3D(horizon[0],horizon[1],horizon[2],'-',color='r',alpha=0.4)

#Representation of the vector corresponding to the Zenith.
zenith_pointer=np.dot(Rot_z,np.dot(Rot_y,np.array([0,0,1.5])))

ax.quiver(-zenith_pointer[0],-zenith_pointer[1],-zenith_pointer[2],2*zenith_pointer[0],2*zenith_pointer[1],2*zenith_pointer[2],color='k',arrow_length_ratio=0.07)

#Calculation of the points corresponding to the rising and setting of the sun, and representation of the day and night.
initial_sun_x=x_orbit[index_sun0]
initial_sun_y=y_orbit[index_sun0]
initial_sun_z=z_orbit[index_sun0]

r=np.sqrt(initial_sun_x**2+initial_sun_y**2)
z_c=initial_sun_z

l_theta=np.linspace(λ+np.pi,λ+3*np.pi,10000)
sun_x=[r*np.cos(x) for x in l_theta]
sun_y=[r*np.sin(x) for x in l_theta]
sun_z=[z_c for x in sun_y]


sun_vectP=vect([sun_x ,sun_y ,sun_z])

day=[x for x in sun_vectP if zenith_pointer[0]*x[0]+zenith_pointer[1]*x[1]+zenith_pointer[2]*x[2]>0]
night=[x for x in sun_vectP if zenith_pointer[0]*x[0]+zenith_pointer[1]*x[1]+zenith_pointer[2]*x[2]<=0]

if day:
    coords_day=coords(day)
    ax.plot3D(coords_day[0],coords_day[1],coords_day[2],'-',color='#3a7707',alpha=0.6)
if night:
    i_salto=int(round(len(night)/2))
    night=night[i_salto+10:]+night[:i_salto-10]
    coords_night=coords(night)
    ax.plot3D(coords_night[0],coords_night[1],coords_night[2],'-',color='#0000ff',alpha=0.6)
if day and night:
    rising=day[1]
    setting=day[-1]
    ax.plot3D(rising[0],rising[1],rising[2],'o',color='k')
    ax.plot3D(setting[0],setting[1],setting[2], 'o',color='k')

    t=np.linspace(0,1,1000)
    x_segment=[]
    y_segment=[]
    z_segment=[]
    for i in range(0,len(t)):
        x_segment.append(rising[0]+t[i]*(setting[0]-rising[0]))
        y_segment.append(rising[1]+t[i]*(setting[1]-rising[1]))
        z_segment.append(rising[2]+t[i]*(setting[2]-rising[2]))
    ax.plot3D(x_segment,y_segment,z_segment,'--',color='k',alpha=0.4)

#Representation of the origin.
ax.plot3D(0,0,0,'ok')

#Add text to indicate the names of the vectors, and the equator.
ax.text(-0.15, 0.05, 1.15, "P", color='k',size='xx-large')
ax.text(zenith_pointer[0], zenith_pointer[1]+0.2, zenith_pointer[2], "Z", color='k',size='xx-large')
ax.text(-0.75, 0.75, 0, " Ecuador", color='k',size='x-small')
ax.text(0, 0, 1.75, datetime.strptime(date, '%m-%d').strftime("%B %d"), color='k',size='medium', bbox=dict(facecolor='none', edgecolor='k', pad=5.0),ha='center')

#Start of the animation process.
#Create a loop, in each loop the graph will be updated and saved.

#Add a time counter
start = time()

#If the folder 'animations' does not exist, it will be created.
if not os.path.exists("./animations"):
    os.makedirs('animations')

with writer.saving(fig,"./animations/rising_setting.mp4",250):
    #Create a loop, in each loop the position of the sun will be updated.
    for i in indexes[:30]:
        print(str(indexes.index(i)+1)+'/'+str(frames))
        temp,=ax.plot3D(x_orbit[i],y_orbit[i],z_orbit[i],'o',color='#fbb506')
        writer.grab_frame()
        temp.remove()

#Display the execution time.
print('Execution time = ' + str(round(time() - start,2)) + ' s')
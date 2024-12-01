import numpy as np
import math as m
import os

G=6.672*(10**-11) #Constante de la gravitación universal
M=1.989*(10**30) #Masa del Sol

#Función asociada al sistema de ecuaciones diferenciales
def f(t,x,y,vx,vy):   
    return [vx, -(x*G*M)/(m.sqrt(x**2+y**2))**3, vy, -(y*G*M)/(np.sqrt(x**2+y**2))**3]

#Defino una función que aplique el algoritmo de Runge-Kutta:
def rk(f,p0,t):
    niter=len(t)-1
    h=t[1]-t[0]
    
    x=np.empty(niter+1)
    vx=np.empty(niter+1)
    y=np.empty(niter+1)
    vy=np.empty(niter+1)
    x[0]=p0[0]
    y[0]=p0[1]
    vx[0]=p0[2]
    vy[0]=p0[3]
    
    
    for n in range(niter):

        C1=f(t[n],x[n],y[n],vx[n],vy[n])
        
        k1=h*(C1[0])
        l1=h*(C1[1])
        q1=h*(C1[2])
        m1=h*(C1[3])

        C2=f(t[n]+h/2,x[n]+k1/2,y[n]+q1/2,vx[n]+l1/2,vy[n]+m1/2)
        k2=h*(C2[0])
        l2=h*(C2[1])
        q2=h*(C2[2])
        m2=h*(C2[3])

        C3=f(t[n]+h/2,x[n]+k2/2,y[n]+q2/2,vx[n]+l2/2,vy[n]+m2/2)
        k3=h*(C3[0])
        l3=h*(C3[1])
        q3=h*(C3[2])
        m3=h*(C3[3])

        C4=f(t[n]+h,x[n]+k3,y[n]+q3,vx[n]+l3,vy[n]+m3)
        k4=h*(C4[0])
        l4=h*(C4[1])
        q4=h*(C4[2])
        m4=h*(C4[3])
        
        x[n+1]=x[n]+1/6*(k1+2*k2+2*k3+k4)
        vx[n+1]=vx[n]+1/6*(l1+2*l2+2*l3+l4)
        y[n+1]=y[n]+1/6*(q1+2*q2+2*q3+q4)
        vy[n+1]=vy[n]+1/6*(m1+2*m2+2*m3+m4)
        
    return [x, y, vx, vy]

# Función que toma como argumentos la longitud del semieje mayor, la excentricidad de la órbita y el argumento del periastro,
# y devuelve los datos iniciales para solucionar el sistema de ecuaciones diferenciales
def estado_inicial(u, e, theta):
    """  
     u := Longitud del semieje mayor medido en unidades astronómicas (UA)
     e := Excentricidad de la órbita
     theta := Argumento del periastro

     A partir de las tres variables asociadas a un planeta, la función calcula los valores de posición y velocidad en su afelio,
     lo cual nos proporciona valores inicales para nuestro problema de valores iniciales.

     La función devuelve un vector que contiene:
     
     1-> x0: Componente x de la posición inicial
     2-> y0: Componente y de la posición inicial
     3-> v0_x: Componente x de la velocidad inicial
     4-> v0_y: Componente y de la velocidad inicial
    """    
    G=6.672*(10**-11) #Constante de la gravitación universal
    M=1.989*(10**30) #Masa del Sol
    
    sol = np.empty(4) #Creamos el vector que contendrá los cuatro valores iniciales (posición y velocidad)
    
    alpha = (theta - 180) * 2 * np.pi / 360 #Calculamos alpha, que será el argumento del apoastro o afelio
    a = u * 149597870700 #Longitud del semieje mayor medido en metros
    dist_afelio=a*(1+e) #Longitud del vector posición en el afelio
    v = np.sqrt(G * M / a * (1 - e) / (1 + e)) #Módulo del vector velocidad en su afelio
    
    sol[0] = np.cos(alpha)*dist_afelio #x0
    sol[1] = np.sin(alpha)*dist_afelio #y0
    sol[2] = v * np.cos(np.pi / 2 + alpha) #v0_x
    sol[3] = v * np.sin(np.pi / 2 + alpha) #v0_y
    return sol


# Definimos los valores iniciales para la Tierra
u=1
excentricidad=0.0167
theta=180

estado_inicial_tierra = estado_inicial(u, excentricidad, theta)

# Definimos el intervalo de tiempo entre cada punto de la orbita en segundos.
interval_tiempo_aprox=30

particiones=m.trunc((365*24*3600)/interval_tiempo_aprox)
interval_tiempo_real=(365*24*3600)/particiones

# Calcula el punto del solsticio de verano.
punto_solsticio= int(np.round(particiones-(15*24*3600+5*3600+8*60)/interval_tiempo_real))

# Establecemos un año como el tiempo final.
Tf_dias=365 # 1 año
Tf=Tf_dias*24*3600
t = np.linspace(0, Tf, particiones)

# Aplico Runge-Kutta para calcular los puntos de laórbita
mov_tierra2 = rk(f, estado_inicial_tierra, t)

# Establezco como primer punto el correspondiente al solsticio.
l0_0=mov_tierra2[0][punto_solsticio:]
l0_1=mov_tierra2[0][:punto_solsticio]
l1_0=mov_tierra2[1][punto_solsticio:]
l1_1=mov_tierra2[1][:punto_solsticio]

# Creo la lista de los vectores posición.
mov_tierra=[np.concatenate([l0_0,l0_1],axis=None),np.concatenate([l1_0,l1_1],axis=None)]


# Guardo los datos en el fichero posicion1.csv
i=0
text2save=[]
while i<len(mov_tierra[0]):
    an=str(mov_tierra[0][i])+','+str(mov_tierra[1][i])
    text2save.append(an)
    i=i+1


ruta='./datos/posicion1.csv'

if not os.path.exists("./datos"):
    os.makedirs('datos')

file=open(ruta,'w')
file.writelines('\n'.join(text2save))
file.close()
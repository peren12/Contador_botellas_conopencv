from __future__ import print_function
import threading
import psycopg2
import pprint
import sys
from time import time
import numpy as np
import cv2
from Tkinter import*

global edges
global contador
contador = 0
global defec
defec = 0
global ventana
global t1
global obj
global objCursor
global captura

   
def Captura():
    global contador
    global defec
        
    # NOTA: cv2.findContours este metodo destruye la imagen
    cnts, hier = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Cuantos contornos se encuentran?
    print("Se encontro {} botellas".format(len(cnts)))   
    a = int(len(cnts))
    contador = contador + a
    #si no hay botellas que empiece a contar los errores
    if a == 0 or a == 1:
        defec+=1;
    print("Total de botellas {}".format(contador))
    
  
def Datos():
    global ventana
    global contador
    global defec
    ##Crea la ventana hija
    t1 = Toplevel(ventana)

    ##Establece el tamo de la ventana
    t1.geometry("200x300+0+0")
    t1.title("Base de Datos")

    ##Provoca que la ventana tome el focus
    t1.focus_set()

    ##Deshabilita todas las otras ventanas hasta que se cierre o destruya
    t1.grab_set()

    #Indica que la ventana es de tipo transient,aparece al frente del padre
    t1.transient(master=ventana)
    #Nombre de la linea
    etiqueta3 = Label(t1, text ='POSTGREES',font=('Verdana',14)).place(x=85,y=4)
    etiqueta4 = Label(t1, text ='No de botellas vistas: ',font=('Verdana',11)).place(x=20,y=40)
    etiqueta5 = Label(t1, text ='No de errores: ',font=('Verdana',11)).place(x=20,y=60)
    #etiqueta6 = Label(t1, text ='No de botellas con tapadera: ',font=('Verdana',11)).place(x=20,y=80)
    etiqueta7 = Label(t1, text ='Total de botellas: ',font=('Verdana',11)).place(x=20,y=100)
    #Numero de botellas #Aun falta otra variable global aparte de contador
    etiqueta4 = Label(t1, text =contador,font=('Verdana',11)).place(x=240,y=40)
    etiqueta5 = Label(t1, text =defec,font=('Verdana',11)).place(x=240,y=60)
    #etiqueta6 = Label(t1, text =contador,font=('Verdana',11)).place(x=240,y=80)
    etiqueta7 = Label(t1, text =contador,font=('Verdana',11)).place(x=240,y=100)

    #Ejecutar consultas a la BD
    objCursor=obj.cursor()

    #Comando para inserar datos en tabla
    objCursor.execute("INSERT INTO registro(botellas, defectuosas, total) VALUES(%s,%s,%s)",(contador, defec, contador))
        
    #Comando para guardar en tabla
    obj.commit()
    
    #Comando para ver tabla
    objCursor.execute("SELECT botellas, defectuosas, total FROM registro ORDER BY id DESC LIMIT 1")
    #Comando para leer registros no para guardar datos
    registros=objCursor.fetchall()

    #imprimir los registros
    pprint.pprint(registros)
    
    #Metodo destroy de la misma ventana
    Button(t1,text="Cerrar", command=t1.destroy).place(x=130,y=150)

    #Pausa el mainloop de la venta de donde se hizo la invocacion
    t1.wait_window(t1)

def Salir():
    global ventana
    global obj
    objCursor.close()
    obj.close()
    ventana.destroy()
    cv2.destroyAllWindows()
    
def Conexion():
        global obj
        global objCursor
        global contador
        global defec
        #Variable de conexion
        cadenaConexion="host='localhost' dbname='proyecto' user='postgres' password='12345'"
        #imprimir cadena conexion
        print("Cadena conexion a la BD \n ->%s"%(cadenaConexion))

        obj=psycopg2.connect(cadenaConexion)

        #Ejecutar consultas a la BD
        objCursor=obj.cursor()
    
        #Comando para inserar datos en tabla
        objCursor.execute("INSERT INTO registro(botellas, defectuosas, total) VALUES(%s,%s,%s)",( contador,defec,contador))
        
        #Comando para guardar en tabla
        obj.commit()


def Vista():
    global edges
    global captura
    #Inicia Captura de Camara
    captura = cv2.VideoCapture(0)
    while(1):

        #Capturar una imagen y Mostrarla
        _, imagen = captura.read()
        
        cv2.imshow('Color Real',imagen)
        cv2.resizeWindow('Color Real', 640, 480)
        
        #Conversion de Imagen a Escala HSV 
        hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

        #Hue Satu Value
        #Guardamos el rango de colores hsv (azules)
        bajos = np.array([105, 120, 105], dtype=np.uint8)   #67,40,105 default
        altos = np.array([129, 255, 182], dtype=np.uint8)   #129,255,182 default
     
        #Crear una mascara que detecte los colores
        mask = cv2.inRange(hsv, bajos, altos)

        #Filtrar el ruido con un CLOSE seguido de un OPEN --Kernel Filtrar o Convolucionar
        kernel = np.ones((8,8),np.uint8) #Valores de 8 bits
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
     
        #Difuminamos la mascara para suavizar los contornos y aplicamos filtro canny
        blur = cv2.GaussianBlur(mask, (3, 3), 0)    #default 5,5
        edges = cv2.Canny(mask,1,150)               #default 1 y 3 
        cv2.imshow('Contorno',edges)

        tecla = cv2.waitKey(5) & 0xFF
        if tecla == 27: #Si se presiona ESC salir
            captura.release()#liberar 
            cv2.destroyAllWindows()
            break
  
def Ventana():
    global ventana
    ##Creacion de Ventana
    ventana=Tk()
    ventana.geometry("330x270+50+50")
    #ventana = Frame(height = 200, width=200)
    ventana.title("Proyecto")
    #ventana.pack(padx = 60, pady = 40)

    ##Mensaje de Bienvenida
    etiqueta = Label(text ='PROYECTOS AIE',font=('Verdana',14)).place(x=85,y=4)
    etiqueta2 = Label(text ='CONTROL DE CALIDAD',font=('Verdana',14)).place(x=50,y=40)

    ##Creacion de Botones
    boton1 = Button(ventana, command = Captura, text='Captura', font=('Verdana',15)).place(x = 50, y = 90)
    boton2 = Button(ventana, command = Datos, text='Datos', font=('Verdana',15)).place(x = 170, y = 90)
    boton3 = Button(ventana, command = Salir, text='Salir', font=('Verdana',15)).place(x = 125, y = 160)
    boton4 = Button(ventana, command = reiniciar, text='Reiniciar Registro', font=('Verdana',15)).place(x = 60, y = 210)

    ventana.mainloop()

def main():
    print('Inicializando')
    #Hilo de Ventana Tkinter
    hilo1 = threading.Thread(target = Ventana, args=())
    hilo1.start()
    #Hilo de Ventana Visualizar Camara
    hilo2 = threading.Thread(target = Vista, args=())
    hilo2.start()
    #Hilo de POSTGRESS
    #hilo3 = threading.Thread(target = Conexion, args=())
    #hilo3.start()

def reiniciar():
    global contador
    global obj
    global objCursor
    global defec
    contador = 0
    defec = 0
    objCursor.execute("TRUNCATE TABLE registro")
    obj.commit()
     
main()







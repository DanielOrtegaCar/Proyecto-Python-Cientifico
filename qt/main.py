import os
import sys
from PyQt5 import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import *
from pyqtgraph import QtGui
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
import funciones as f
# import matplotlib as plt
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# plt.use("Qt5Agg")
from matplotlib import rcParams
from matplotlib.figure import Figure
rcParams['font.size'] = 9
import numpy as np
import pandas as pd
import random
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
# variables


# definimos una clase para crear una nueva ventana de dialogo
class DescargaDatos(QtGui.QDialog):
    # constructor de la clase en el, seleccionamos la interfaz a que deseamos
    # que sea mostrada, luego debemos conectar los elementos de las interfazs
    # a los metodos

    def __init__(self):

        super(DescargaDatos, self).__init__()
        os.chdir(ruta_principal)
        self.ui = loadUi('interfaz/descarga_datos.ui', self)

        ultimo = soluciones_cmt.shape[0] - 1

        # dejamos un valor predeterminado, que corresponde a la fecha actual
        self.ui.fecha_inicio_edit.setDate(soluciones_cmt['fecha_evento'][0])
        self.ui.fecha_termino_edit.setDate(
            soluciones_cmt['fecha_evento'][ultimo])
        # al pinchar el boton se ejecuta el meotodos
        self.datos_Button.clicked.connect(self.enviar_datos)
        
        # self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # deja un valor predeterminado que corresponde a 5
        self.ui.magnitud_edit.setText("5")
        self.ui.radiomin_Edit.setText("50")
        self.ui.radiomax_lineEdit.setText("90")
        self.ui.start_time_lineEdit.setText("60")
        self.ui.end_time_lineEdit.setText("3600")
        self.ui.dist_esta_lineEdit.setText("1000")

    

        # transformamos los strings a fechas

        # print(type(self.soluciones['fecha_evento']))
        # print(type(self.soluciones['fecha_evento'][0].dt.date))

    # realizamos una llamada al metodo descargar_datos datos, cuando se
    # seleeciona un elemento en la lista, previamente cargados por
    # enviar_datos
    def print_info(self):

        numero = self.ui.descargar_listWidget.row(
            self.ui.descargar_listWidget.currentItem()) 
        numero  = self.a_mostrar[numero]
        # try:s
        # print(self.a_mostrar[numero])
        resultados = soluciones_cmt[soluciones_cmt["Unnamed: 0"] == numero]
        codigo= f.descargar_datos(resultados,0,0)
        if (codigo == -100):
            QtGui.QMessageBox.information(self, "Error", "Datos descargados anteriormente")
        else:
            QtGui.QMessageBox.information(self, "Exito", "Datos descargados exitosamente")
        # except:
        # QtGui.QMessageBox.information(
        # self, " ", "No se encontraron registros para los datos
        # seleccionados")

        self.done(0)

    # llamamos al metodo enviar_datos, para descargar la informacion asociado
    # a los datos y cargarlos en una lista, para luego poder ser seleecionados
    def enviar_datos(self):
        self.ui.descargar_listWidget.clear()
        temp_var = self.ui.fecha_inicio_edit.date()
        fecha_inicio = temp_var.toPyDate()
        temp_var = self.ui.fecha_termino_edit.date()
        fecha_termino = temp_var.toPyDate()
        magnitud = int(self.ui.magnitud_edit.text())

        self.datos = f.pedir_datos(soluciones_cmt, fecha_inicio, fecha_termino)
        if(len(self.datos) == 0):
            QtGui.QMessageBox.information(
                self, " ", "Busqueda no ha arrojado resultados")
        self.a_mostrar = []
        for i, region, mw, lat, lon in zip(self.datos["Unnamed: 0"], self.datos["region"], self.datos["Mw_cmt"], self.datos["lat_cmt"], self.datos["lon_cmt"]):
            mw = np.around(mw, 2)
            string = str(region) + "  Mw: " + str(mw)
            self.a_mostrar.append(i)
            self.ui.descargar_listWidget.addItem(string)
        self.ui.descargar_listWidget.currentItemChanged.connect(
            self.print_info)
        # clickeado = self.ui.descargar_listWidget.itemClicked.connect(self.ui.descargar_listWidget.listClicked)
        # print(clickeado)


# Ventana de dialogo para seleccionar el evento que queremos graficar
class SeleccionarDatos(QtGui.QDialog):

    # cargamos lista de datos, cargados en el programa, para luego ser
    # retornado el indice escogido, para ser graficado en la interfaz
    # principal del programa
    def __init__(self, waveforms):
        super(SeleccionarDatos, self).__init__()
        self.ui = loadUi('interfaz/seleccionar.ui', self)
        self.waveforms = waveforms
        for element in self.waveforms:
            string = element.__dict__["stats"].network + \
                " " + element.__dict__["stats"].station
            self.ui.indice_listWidget.addItem(string)
        self.seleccionar_Button.clicked.connect(self.print_info)

    # funcion que retona el numero seleccionado, en la lista
    def print_info(self):
        self.numero = self.ui.indice_listWidget.row(
            self.ui.indice_listWidget.currentItem())
        self.done(self.numero)

# ventana principal de la aplicacion se define los metodos y el espacio
# para realizar graficos


class MainWindow(QtGui.QMainWindow):

    # asociamos eventos a apretar los botones, que corresponden a llamadas de
    # funciones
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = loadUi('interfaz/main_windows.ui', self)
        self.m = PlotCanvas(self, width=5, height=4)
        self.m.setGeometry(QtCore.QRect(60, 50, 501, 471))
        self.descargar_Button.clicked.connect(self.executeDescargaDatos)
        self.cargar_estaciones_Button.clicked.connect(self.path_estaciones)
        self.mapa_Button.clicked.connect(self.graficar_mapa)
        self.cargar_waveforms_Button.clicked.connect(self.path_waveforms)
        self.remover_respuesta_Button.clicked.connect(self.remover_respuesta)
        self.filtrar_ondap_Button.clicked.connect(self.remover_respuesta)
        self.graficar_Button.clicked.connect(self.executeSeleccionarDatos)
        self.limpiar_datos_pushButton.clicked.connect(self.limpiar_valores)
        self.guardar_cambios_pushButton.clicked.connect(self.limpiar_valores)
        self.sismograma_pushButton.clicked.connect(self.sismograma_sintetico)
        self.pick_pushButton.clicked.connect(self.pick)
        self.waveforms = ""
        self.estaciones = ""

    def sismograma_sintetico(self):
        tipo = "basico"
        self.sismograma_sintetico = f.generar_sintetico(tipo,self.ruta_info,soluciones_cmt,self.bulk)

    def pick(self):
        print("asd")


    def limpiar_valores(self):
        self.waveforms = ""
        self.estaciones = ""
        self.file_estaciones = ""
        self.estaciones = ""
        self.file_waveforms = ""
        self.waveforms = ""
        self.bulk = ""
        self.sismograma_sintetico = ""
        QtGui.QMessageBox.information(self, "Exito ", "Datos limpiados correctamente")

    def guardar_cambios(self):
        
        QtGui.QMessageBox.information(self, "Exito ", "Datos guardados correctamente")        

        # metodo que llama a un instancia de DescargaDatos, y muestra la
        # pantalla, la ejecuccion del metodo exec_(), permite retonar valores
        # de los dialogos
    def executeDescargaDatos(self):
        descarga_datos_windows = DescargaDatos()
        descarga_datos_windows.exec_()
        # pasar datos de un dialog a otro
        # print(descarga_datos_windows.magnitud_edit.text())

        # metodo que llama a un instancia de SeleccionarDatos, y muestra la
        # pantalla, la ejecuccion del metodo exec_(), permite retonar valores
        # de los dialogos
    def executeSeleccionarDatos(self):
        if (type(self.waveforms) is not type(" ")):
            seleccionar_datos_windows = SeleccionarDatos(self.waveforms)
            seleccionar_datos_windows.exec_()
            # recibimos valor de qdialog
            self.indice_array = seleccionar_datos_windows.numero
            self.graficar(self.indice_array)
            self.m.plot(self.waveforms[0])
        else:
            QtGui.QMessageBox.information(
                self, "Error ", "Seleecione carpeta waveforms")

    # cargamos una interfaz, para seleccionar el una carpeta, donde se
    # encuentran almacenadas las estaciones, para luego ser cargadas
    def path_estaciones(self):
        self.file_estaciones = str(QtGui.QFileDialog.getExistingDirectory(
            self, "Seleccione estaciones"))
        self.ruta_info = self.file_estaciones.replace("/stations","")

        if self.file_estaciones:
            self.estaciones,self.bulk,self.fallas= f.cargar_stations(self.file_estaciones,soluciones_cmt,self.ruta_info)
            
            if(np.size(self.estaciones) == 0):
                QtGui.QMessageBox.information(
                    self, "Error ", "Seleecione carpeta estaciones")
            else:
                QtGui.QMessageBox.information(
                    self, "Exito", "Archivos cargados correctamente")

   # cargamos una interfaz, para seleccionar el una carpeta, donde se
   # encuentran almacenadas las waveforms para luego ser cargadas
    def path_waveforms(self):
        self.file_waveforms = str(QtGui.QFileDialog.getExistingDirectory(
            self, "Seleccione waveforms"))
        if self.file_waveforms:
            # print(self.file_estaciones)
            self.waveforms = f.cargar_waveforms(self.file_waveforms,self.fallas)
            # print(self.waveforms)
            if(np.size(self.waveforms) == 0):
                QtGui.QMessageBox.information(
                    self, "Error ", "Seleecione carpeta waveforms")
            else:
                QtGui.QMessageBox.information(
                    self, "Exito", "Archivos cargados correctamente")

        # funcion que realiza los checks necesarios para llamar al metodo
        # remover_respuesta, si existen archivos cargados, nos permite llamar a
        # la funcion, de otra manera, nos indicara que debemos cargar los
        # archivos
    def remover_respuesta(self):
        if(type(self.waveforms) is type(" ") or type(self.estaciones) is type(" ")):
            QtGui.QMessageBox.information(
                self, "Error ", "Primero cargue los datos")
        else:
            self.waveforms = f.remover_respuesta(self.waveforms,self.estaciones)
            QtGui.QMessageBox.information(
                self, "Exito", "Operacion realizada correctamente")
        # funcion que realiza los checks necesarios para llamar al metodo
        # periodo_P, si existen archivos cargados, nos permite llamar a
        # la funcion, de otra manera, nos indicara que debemos cargar los
        # archivos

    def periodo(self):
        # print(self.file_waveforms, self.estaciones)
        if(type(self.waveforms) is type(" ") or type(self.estaciones) is type(" ")):
            QtGui.QMessageBox.information(
                self, "Error ", "Primero cargue los datos")
        else:
            tipo = "bandpass"
            self.waveforms = f.filtro(tipo,self.waveforms)
            QtGui.QMessageBox.information(
                self, "Exito", "Operacion realizada correctamente")

        # funcion que realiza los checks necesarios para llamar al metodo
        # graficar, si existen archivos cargados, nos permite llamar a
        # la funcion y se actualiza el grafico, de otra manera, nos indicara que debemos cargar los
        # archivos
    def graficar(self, numero):
                # if(type(self.waveforms) is type(" ")):
        try:
            self.m.plot(self.waveforms[numero])
            QtGui.QMessageBox.information(
                self, " ", "Datos graficos exitosamente")
        except:
            QtGui.QMessageBox.information(
                self, "Error ", "Primero cargue los datos")

    def graficar_mapa(self):
        ruta = os.getcwd() + "/interfaz/estaciones.png"
        if self.file_estaciones:
            f.mapa(self.file_estaciones, ruta)
        else:
            QtGui.QMessageBox.information(
                self, "Error ", "Cargue waveforms y stations del evento")

# clase definida, para definir un lugar donde se pueda graficar en la interfaz


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # funcion para actualizar el grafico, ademas si se quieren definir
    # distintos estilos de graficos se puede modificar aqui, agregando o
    # eliminando parametros
    def plot(self, st):
        tr = st
        print(tr)
        ax = self.figure.add_subplot(111)
        ax.plot(tr.times("matplotlib"), tr.data, "b-")
        ax.xaxis_date()
        self.figure.autofmt_xdate()
        self.draw()


# llama a la ejecuccion de la ventana principal dando inicio a la aplicaicon
ruta_principal = os.getcwd()
ruta_soluciones = ruta_principal + "/datos/cmt.csv"
soluciones_cmt = pd.read_csv(ruta_soluciones, low_memory=False)
soluciones_cmt['fecha_evento'] = pd.to_datetime(soluciones_cmt['fecha_evento'])
soluciones_cmt['fecha_evento'] = soluciones_cmt['fecha_evento'].dt.date
app = QtGui.QApplication(sys.argv)
widget = MainWindow()
widget.show()
sys.exit(app.exec_())

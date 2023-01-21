#!/usr/bin/env python
import sys
import serial
import time
import pygame
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QCompleter,QButtonGroup, QTableView,QLineEdit, \
    QTableWidget, QTableWidgetItem
#from PyQt5.QtSql import *
from PyQt5 import uic,QtGui,QtCore,QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate,Qt,pyqtSlot, QObject
from PyQt5.QtGui import QPainter, QColor, QFont, QImage
import gtts
import contactos
#from text2speech import t2s
import os

ser = serial.Serial("/dev/ttyAMA0", 9600, timeout = 15)

def SIM800(command):
    AT_command = command + "\r\n"
    ser.write(str(AT_command).encode('ascii'))
    time.sleep(1)
    if ser.inWaiting() > 0:
        echo = ser.readline() #waste the echo
        response_byte = ser.readline()
        response_str = response_byte.decode('ascii')
        return (response_str)
    else:
        return ("ERROR")

#Checks SIM800L status and connects with ShopifyAPI
def Init_GSM():
    if "OK" in SIM800("AT"):
        if ("OK" in (SIM800("AT+CLCC=1"))) and ("OK" in (SIM800("AT+DDET=1"))) and ("OK" in (SIM800("AT+CNMI =0,0,0,0,0"))) and ("OK" in (SIM800("AT+CMGF=1"))) and ("OK" in (SIM800("AT+CSMP=17,167,0,0"))):  # enble DTMF / disable notifications
            print("SIM800 Module -> Active and Ready")
    else:
        print("------->ERROR -> SIM800 Module not found")

def wait_for_SIM800():
    echo = ser.readline()  # waste the echo
    response_byte = ser.readline()
    response_str = response_byte.decode('ascii')
    return (response_str)

def p_audio():

    pygame.mixer.pre_init(28050, -16, 2, 1024) # setup mixer to avoid sound lag
    pygame.init()
    pygame.mixer.init()
    #time.sleep(2)
    pygame.mixer.music.load('p1.mp3')
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
    
        pygame.time.Clock().tick(10)

def Call_response_for (phone_number):
    AT_call = "ATD" + phone_number + ";"
    response = "NONE"
    time.sleep(1)
    ser.flushInput() #clear serial data in buffer if any
    if ("OK" in (SIM800(AT_call))) and (",2," in (wait_for_SIM800())) and (",3," in (wait_for_SIM800())):
        print("RINGING...->", phone_number)
        call_status = wait_for_SIM800()
        if "1,0,0,0,0" in call_status:
            print("**ANSWERED**")
            ser.flushInput()
            #play_wav("intro.wav")
            p_audio()

            time.sleep(0.5)
            dtmf_response = "start_over"
            SIM800("ATH")
            
            
            while dtmf_response == "start_over":
                #play_wav("press_request.wav")
                time.sleep(1)
                dtmf_response = wait_for_SIM800()
                if "+DTMF: 1" in dtmf_response:
                    #play_wav("confirmed.wav")
                    response = "CONFIRMED"
                    hang = SIM800("ATH")
                    break
                if "+DTMF: 2" in dtmf_response:
                    #play_wav("canceled.wav")
                    response = "CANCELED"
                    hang = SIM800("ATH")
                    break
                if "+DTMF: 9" in dtmf_response:
                    #play_wav("callback_response.wav")
                    response = "REQ_CALLBACK"
                    hang = SIM800("ATH")
                    break
                if "+DTMF: 0" in dtmf_response:
                    dtmf_response = "start_over"
                    continue
                if "+DTMF: " in dtmf_response:
                    #play_wav("invalid_input.wav")
                    dtmf_response = "start_over"
                    continue
                else:
                    response = "REJECTED_AFTER_ANSWERING"
                    break
        else:
            #print("REJECTED")
            response = "CALL_REJECTED"
            hang = SIM800("ATH")
            time.sleep(1)
            #ser.flushInput()
    else:
        #print("NOT_REACHABLE")
        response = "NOT_REACHABLE"
        hang = SIM800("ATH")
        time.sleep(1)
        #ser.flushInput()
    ser.flushInput()
    return (response)

class Ventana(QMainWindow):
#---------------------------------------------------------------------------------------# Inicio de ventana 
    def __init__(self):
        QMainWindow.__init__(self)

        self.MainWindow1=loadUi("mainWindow.ui",self)
        
        self.Opcion=2

        self.camiones=['','1Turbo','2Sencillo','3Doble Troques','Todos','Test']

        self.BotonLlamada.clicked.connect(self.Llamada)
        self.B_estandar.clicked.connect(self.Men_estandar)
        self.B_personalizado.clicked.connect(self.Men_personalizado)


        self.TCamion.addItems(self.camiones)
        
        #self.resumenPaciente.setEnabled(False)
        #self.nuevoRegistro.setEnabled(False)

        Init_GSM()

    def Men_estandar(self):

        # self.CargaT.clear()
        # self.PesoT.clear()
        # self.LugarIT.clear()
        # self.LugarFT.clear()
        # self.HoraIT.clear()
        # self.HoraFT.clear()

        self.Opcion=1

        self.CargaT.setEnabled(True)
        self.PesoT.setEnabled(True)
        self.LugarIT.setEnabled(True)
        self.LugarFT.setEnabled(True)
        self.HoraIT.setEnabled(True)
        self.HoraFT.setEnabled(True)

        self.Text_pers.setEnabled(False)

    def Men_personalizado(self):
        # self.Text_pers.clear()

        self.Opcion=2

        self.CargaT.setEnabled(False)
        self.PesoT.setEnabled(False)
        self.LugarIT.setEnabled(False)
        self.LugarFT.setEnabled(False)
        self.HoraIT.setEnabled(False)
        self.HoraFT.setEnabled(False)

        self.Text_pers.setEnabled(True)

    def Llamada(self):

        self.LabelLlamada.setText('Linea ocupada')
        QApplication.processEvents()

        camion=self.TCamion.currentText() 

        if self.Opcion == 1:

             
            peso=self.PesoT.text()
            lugari=self.LugarIT.text()
            lugarf=self.LugarFT.text()
            carga=self.CargaT.text()
            horai=self.HoraIT.text()
            horaf=self.HoraFT.text()
            
            texto=f'.Buen dia. se solicita un camion de carga. {carga}. de. {peso}. para cargar en. {lugari}. y descargar en. {lugarf}. para recoger el dia. {horai}. y descargar el dia. {horaf}. para mas informacion revisar nuestro chat de whatsapp. '
            
        else:

            texto=self.Text_pers.text()

        try:

            tts = gtts.gTTS(texto, lang="es", tld="com.mx")
            tts.save("p1.mp3")

            if camion == '':

                print('Por favor elige una opcion valida')

            else:

                print(contactos.contacts(camion))

                for x in contactos.contacts(camion):
                    print(Call_response_for(x))

                print("-----------------------")

        except AssertionError:

            print('Por favor escribe un mensaje')

        self.LabelLlamada.setText('Linea libre')

app = QApplication(sys.argv)
_ventana = Ventana()
_ventana.show()
app.exec_()
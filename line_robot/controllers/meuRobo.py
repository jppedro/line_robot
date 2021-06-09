# line_robot for TI502
# Christovam Alves Lemos - 18192
# Henrique Esteban da Rocha - 18191
# João Pedro Rodrigues da Costa - 19181
import struct
import socket
import sys
import _thread
import os

from controller import Robot, GPS
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont,ImageOps

print("Iniciando")

velocity = 2
timestep = 64

def get_port():
    return 8080

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255',1))    
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    return IP

def servidor(https, hport):
    sockHttp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockHttp.bind((https, hport))
    except:
        sockHttp.bind(('', hport))
        
    sockHttp.listen(1)
    
    while True:
        client, addr = sockHttp.accept()
        _thread.start_new_thread(on_new_client, (client,addr))



class MeuRobot:
    def __init__(self, robot):
        
        self.robot = robot
        self.nome  = robot.getName()
        print("Nome do robo : ", self.nome)
        self.front_motor_e = self.robot.getDevice("roda_front_e")
        self.front_motor_d = self.robot.getDevice("roda_front_d")
        self.back_motor_e  = self.robot.getDevice("roda_back_e")
        self.back_motor_d  = self.robot.getDevice("roda_back_d")

        self.front_motor_e.setPosition(float('+inf'))
        self.front_motor_d.setPosition(float('+inf'))
        self.back_motor_e.setPosition(float('+inf'))
        self.back_motor_d.setPosition(float('+inf'))

        self.front_motor_e.setVelocity(velocidade)
        self.front_motor_d.setVelocity(velocidade)
        self.back_motor_e.setVelocity(velocidade)
        self.back_motor_d.setVelocity(velocidade)
        
        # obtem os sensores de linha
        
        self.line_sensor_d = self.robot.getDevice("line_sensor_d")
        self.line_sensor_d.enable(timestep)
        
        self.line_sensor_e = self.robot.getDevice("line_sensor_e")
        self.line_sensor_e.enable(timestep)
        
        # obtem a camera

        self.cv = self.robot.getDevice("camera")
        self.cv.enable(timestep)
        

class TI502(MeuRobot):
    def andar_frente(self): 
        self.front_motor_e.setVelocity(velocidade)
        self.front_motor_d.setVelocity(velocidade)
        self.back_motor_e.setVelocity(velocidade)
        self.back_motor_d.setVelocity(velocidade)
        
    def andar_tras(self): 
        self.front_motor_e.setVelocity(-velocidade)
        self.front_motor_d.setVelocity(-velocidade)
        self.back_motor_e.setVelocity(-velocidade)
        self.back_motor_d.setVelocity(-velocidade)
        
    def virar_direita(self):
        self.front_motor_e.setVelocity(velocidade)
        self.front_motor_d.setVelocity(velocidade)
        self.back_motor_e.setVelocity(0)
        self.back_motor_d.setVelocity(0)
    
    def virar_esquerda(self):
        self.front_motor_e.setVelocity(0)
        self.front_motor_d.setVelocity(0)
        self.back_motor_e.setVelocity(velocidade)
        self.back_motor_d.setVelocity(velocidade)

    def  pararRobo(self, estado):
        self.parado = estado    
    
#programa principal

    def run(self):
    
        while self.robo.step(timestep) != -1:
            left_line = self.line_sensor_e.getValue()
            right_line = self.line_sensor_d.getValue()
            
            if(left_line != 1000 and right_line == 1000)
                self.virar_esquerda()
            
            if(right_line != 1000 and left_line == 1000)
                self.virar_direita()
            
            else:
                self.andar_frente()





robot = Robot()

robot_controler = TI502(robot)

_thread.start_new_thread(servidor, (get_ip(),get_port()))

robot_controler.run()                


# line_robot for TI502
# Christovam Alves Lemos - 18192
# Henrique Esteban da Rocha - 18191
# João Pedro Rodrigues da Costa - 19181
import struct
import socket
import sys
import _thread
import os
import random

from controller import Robot, GPS
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont,ImageOps

print("Iniciando")

velocity = 5
timestep = 64

def get_port():
    return random.randint(1000, 9999)
    #retorna alguma porta entre 1000 e 9999

def get_path(mensagem):
    msg = mensagem.split("/")[1]
    msg = msg.split(" ")[0]
    return msg 
    
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255',1))    
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    return IP

class MeuRobot:
    def __init__(self, robot):
        
        self.robot = robot
        self.nome  = robot.getName()
        
        print("Nome do robo : ", self.nome)
        
        #obtem os motores do robo
        self.front_motor_e = self.robot.getDevice("roda_front_e")
        self.front_motor_d = self.robot.getDevice("roda_front_d")
        self.back_motor_e  = self.robot.getDevice("roda_back_e")
        self.back_motor_d  = self.robot.getDevice("roda_back_d")

        self.front_motor_e.setPosition(float('+inf'))
        self.front_motor_d.setPosition(float('+inf'))
        self.back_motor_e.setPosition(float('+inf'))
        self.back_motor_d.setPosition(float('+inf'))

        self.front_motor_e.setVelocity(velocity)
        self.front_motor_d.setVelocity(velocity)
        self.back_motor_e.setVelocity(velocity)
        self.back_motor_d.setVelocity(velocity)
        
        # obtem os sensores de linha
        
        self.line_sensor_d = self.robot.getDevice("line_sensor_d")
        self.line_sensor_d.enable(timestep)
        
        self.line_sensor_e = self.robot.getDevice("line_sensor_e")
        self.line_sensor_e.enable(timestep)
        
        # obtem a camera

        self.cv = self.robot.getDevice("camera")
        self.cv.enable(timestep)
        

class TI502(MeuRobot):
    
    #funcao para andar para frente
    def andar_frente(self): 
        self.front_motor_e.setVelocity(velocity)
        self.front_motor_d.setVelocity(velocity)
        self.back_motor_e.setVelocity(velocity)
        self.back_motor_d.setVelocity(velocity)
        
    #funcao para andar para tras
    def andar_tras(self): 
        self.front_motor_e.setVelocity(-velocity)
        self.front_motor_d.setVelocity(-velocity)
        self.back_motor_e.setVelocity(-velocity)
        self.back_motor_d.setVelocity(-velocity)
        
    #funcao para virar para direita
    def virar_direita(self, velocidade):
        self.front_motor_e.setVelocity(0)
        self.front_motor_d.setVelocity(-velocidade)
        self.back_motor_e.setVelocity(-velocidade)
        self.back_motor_d.setVelocity(0)
    
    #funcao para virar para esquerad
    def virar_esquerda(self, velocidade):
        self.front_motor_e.setVelocity(-velocidade)
        self.front_motor_d.setVelocity(0)
        self.back_motor_e.setVelocity(-velocidade)
        self.back_motor_d.setVelocity(0)

    def  pararRobo(self, estado):
        self.parado = estado 
    
    #funcao para tirar e salvar a foto da camera
    def tirar_foto(self):
        self.cv.saveImage("foto.jpg", 1)
        #img = self.cv.getImage()
        #im  = Image.frombytes('RGBA', (self.cv.getWidth(), self.cv.getHeight()), img) 
        #imagem = Image.open('foto.jpg')  
        #imagem.paste(im)
        #imagem.save('foto.jpg')
    
#programa principal

    def run(self):
    
       while self.robot.step(timestep) != -1:
            left_line = self.line_sensor_e.getValue()
            right_line = self.line_sensor_d.getValue()
            
            #se o sensor de linha da direita for 0, ou seja, estiver fora da linha, ele vira à direita
            if(left_line != 0 and right_line == 0):
                self.virar_direita(10)
            
            #se o sensor de linha da esquerda for 0, ou seja, estiver fora da linha, ele vira à esquerda
            if(right_line != 0 and left_line == 0):
                self.virar_esquerda(10)
            
            #caso os 2 sensores estejam na linha, segue andando pra frente
            else:
                self.andar_frente()

robot = Robot()

robot_controler = TI502(robot)

#obtem o servidor
def servidor(https, hport):
    print(f"Server em {https}:{hport}")
    sockHttp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sockHttp.bind((https, hport))
    except:
        sockHttp.bind(('', hport))
        
    sockHttp.listen(1)
    
    while True:
        client, addr = sockHttp.accept()
        msg = client.recv(2048).decode("utf-8") 
        path = get_path(msg)
        
        #caso o path seja uma foto, ira abrir a foto
        if(path == "foto"):
            robot_controler.tirar_foto()
            arq = open('foto.jpg', 'rb')
            res = arq.read()
            arq.close()
            
            web = 'HTTP/1.1 200 OK\n'
            web += 'Content-Type: image/jpg\n\n'
            final_res = web.encode('utf-8')
            final_res += res
            client.sendall(final_res)
            client.close()
            
        else: 
            client.close()

#starta a thread
_thread.start_new_thread(servidor, (get_ip(),get_port()))

robot_controler.run()                


import paho.mqtt.client as mqtt
from Tkinter import *


mqttc = mqtt.Client()
mqttc.connect(host='localhost', port=1883)

root=Tk()

def fnbutton1():
    print("button0: FRONT")
    mqttc.publish(topic='errorvals',payload='0', qos=0)
                      
def fnbutton2():
    print("button1: LEFT")
    mqttc.publish(topic='errorvals',payload='1', qos=0)

def fnbutton3():
    print("button2: RIGHT")
    mqttc.publish(topic='errorvals',payload='2', qos=0)

def fnbutton4():
    print("button3: BACK")
    mqttc.publish(topic='errorvals',payload='3', qos=0)

def fnbutton5():
    print("button4: STOP")
    mqttc.publish(topic='errorvals',payload='4', qos=0)
    
topFrame=Frame(root)
topFrame.pack()

b1=Button(topFrame,text="FRONT :1",fg="green",command=fnbutton1)
b2=Button(topFrame,text="LEFT  :2",fg="green",command=fnbutton2)
b3=Button(topFrame,text="RIGHT :3",fg="green",command=fnbutton3)
b4=Button(topFrame,text="BACK  :4",fg="green",command=fnbutton4)
b5=Button(topFrame,text="STOP  :5",fg="red",command=fnbutton5)


b1.grid(row=0,column=1)
b2.grid(row=1,column=0)
b3.grid(row=1,column=2)
b4.grid(row=2,column=1)
b5.grid(row=1,column=1)
root.mainloop()


#1left
#2right
#4stop
#3back
#


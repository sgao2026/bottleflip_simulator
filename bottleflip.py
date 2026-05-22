Web VPython 3.2

# from vpython import *

Tapp = 0 # user determined torque applied
bottle = cylinder(pos=vec(0, 0, 0), size=vec(1,1,1), axis=vec(0, 3, 0), color=color.white)
percent_ice = 0 # percentage of total volume of the bottle
init_height = 0 # initial height of flip

#def com_ind(shape):
 #   x_cor = bottle.pos.x + bottle.size.x

def torque (force, lever_arm):
    return cross(force, lever_arm)
    
def com_pts (mass, pos):
    result = vec(0,0,0)
    for m,p in zip(mass,pos) :
        result = result + (m * p)
    return result / sum(mass)

masses = (10, 0)
poses = (vector(0,1,0), vector(1,0,0))

print(com_pts(masses, poses))

def go(): # runs simulation
    return
def setSliders(evt): # user inputted torque applied
    if evt.id == 'Tapp_slider':
        Tapp = evt.value
    elif evt.id == 'ice_slider':
        percent_ice = evt.value
    elif evt.id == 'height_slider':
        init_height = evt.value
#         print(Tapp)
        
run = button(bind=go(), text='Run')
Tapp_slider = slider(id='Tapp_slider', bind=setSliders, min=0, value=Tapp, max=15, step=0.1, )
ice_slider = slider(id='ice_slider', bind=setSliders, min=0, value=percent_ice, max=1, step=0.01)
height_slider = slider(id='height_slider', bind=setSliders, min=0, value=init_height, max=5, step=0.1)

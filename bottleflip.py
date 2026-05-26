# Web VPython 3.2

from vpython import *

Tapp = 0 # user determined torque applied
bottle1 = cylinder(pos=vec(0, 0, 0), size=vec(1,1,1), axis=vec(0, 3, 0), color=color.white, opacity=0.5)
percent_ice = 0 # percentage of total volume of the bottle
init_height = 0 # initial height of flip

def com_ind(shape):
    com = sphere(pos=vec(shape.pos + shape.axis/2), color=color.green, radius=0.1)
    return com
com_ind(bottle1)
bottle2 = compound([bottle1, com_ind(bottle1)])

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
    global Tapp, percent_ice, init_height
    if evt.id == 'Tapp_slider':
        Tapp = evt.value
        Tapp_label.text = '{:.2f}\n\n'.format(Tapp)
    elif evt.id == 'ice_slider':
        percent_ice = evt.value
        ice_label.text = '{:.2f}\n\n'.format(percent_ice)
    elif evt.id == 'height_slider':
        init_height = evt.value
        height_label.text = '{:.2f}\n\n'.format(init_height)
#     print(str(evt.id) + " " + str(Tapp))

# sliders + labels
run = button(bind=go(), text='Run', pos=scene.title_anchor)

scene.caption = "Simulation Properties\n\n"

scene.append_to_caption('Select applied torque\n')
Tapp_slider = slider(id='Tapp_slider', bind=setSliders, min=0, value=Tapp, max=15, step=0.1, )
Tapp_label = wtext(text='{:.2f}\n\n'.format(Tapp_slider.value))

scene.append_to_caption('Select amount of ice\n')
ice_slider = slider(id='ice_slider', bind=setSliders, min=0, value=percent_ice, max=1, step=0.01)
ice_label = wtext(text='{:.2f}\n\n'.format(ice_slider.value))

scene.append_to_caption('Select height of release\n')
height_slider = slider(id='height_slider', bind=setSliders, min=0, value=init_height, max=5, step=0.1)
height_label = wtext(text='{:.2f}\n\n'.format(height_slider.value))

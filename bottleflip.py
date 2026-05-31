Web VPython 3.2

#from vpython import *

first = vec(1,0,0)
second = vec(0,1,0)
third = vec(0,0,1)

bottle_mass = 0.036
ice_density = 917 # kg/m^3

scene.camera.pos = vec(0,0.1,1)

t = 0.00
dt = 0.02 # always increment time by 0.01
flips = 0

Tapp = 0 # user determined torque applied
percent_ice = 0.5 # percentage of total volume of the bottle
init_height = 0 # initial height of flip

def vol(shape): # cylinders only
    return pi * shape.radius**2 * shape.length

def com_ind(shape):
    com = sphere(pos=vec(shape.pos + shape.axis/2), color=color.green, radius=0.01, visible = False)
    return com

def torque (force, lever_arm):
    return cross(force, lever_arm)
    
def com_pts (mass, pos):
    result = vec(0,0,0)
    for m,p in zip(mass,pos) :
        result = result + (m * p)
    return result / sum(mass)

bottle_ice = group()
bottle = cylinder(pos=vec(0, 0, 0), radius=0.03175, length=.203, axis=second, color=color.white, opacity=0.5, group=bottle_ice)
ice = cylinder(pos=bottle.pos, radius=bottle.radius, length=bottle.length * percent_ice, axis=bottle.axis, color=color.cyan, opacity=0.5, group=bottle_ice)

bottle_com = com_ind(bottle)
ice_com = com_ind(ice)
bottle_com.group = bottle_ice
ice_com.group = bottle_ice

bottle_ice_com = sphere(pos=com_pts((bottle_mass, vol(ice) * ice_density), (bottle_com.pos, ice_com.pos)), color=color.red, radius=0.01, group=bottle_ice)

def draw_parabola (v_initial,  a_y = -10):
    global t, bottle_ice, bottle_ice_com
    v_x = dot(v_initial, first)
    v_y = dot(v_initial, second)
    
    x = dot(bottle_ice.pos, first)
    y = dot(bottle_ice.pos, second)
    
    trace = attach_trail(bottle_ice_com, color=color.green)
    while y > 0:
        rate(1 / dt)
        x = x + v_x * dt
        
        v_y = v_y + a_y * dt
        y = y + v_y * dt
        
        bottle_ice.pos = vec(x, y, 0)
        
        xDots.plot(t,x)
        yDots.plot(t,y)
        akDots.plot(t,0)
        tkDots.plot(t, 0.5 * (pi * dot(bottle.size, first) * dot(bottle.size, second)**2 + pi * dot(ice.size, first) * dot(ice.size, second)**2) * sqrt(v_x**2 + v_y**2))
        
        t = t + dt
    trace.stop()
    return

init_pos = bottle_ice.pos
def go(): # runs simulation
    global bottle_ice, run
    
    run.text = 'Pause'
    
    bottle_ice.pos = init_pos # resetting
    draw_parabola(v_initial=vec(5,10,0))
    
    run.text = 'Run'
    return

def setSliders(evt): # user inputted torque applied
    global Tapp, percent_ice, init_height, ice, ice_com, bottle, bottle_ice_com
    if evt.id == 'Tapp_slider':
        Tapp = evt.value
        Tapp_label.text = '{:.2f}\n\n'.format(Tapp)
    elif evt.id == 'ice_slider':
        percent_ice = evt.value
        ice_label.text = '{:.2f}\n\n'.format(percent_ice)
        
        ice.axis = second
        ice.length = bottle.length * percent_ice
        ice_com.pos = com_ind(ice).pos
        bottle_ice_com.pos = com_pts((bottle_mass, vol(ice) * ice_density), (bottle_com.pos, ice_com.pos))
    elif evt.id == 'height_slider':
        init_height = evt.value
        height_label.text = '{:.2f}\n\n'.format(init_height)
#     print(str(evt.id) + " " + str(Tapp))

# sliders + labels
run = button(bind=go, text='Run', pos=scene.title_anchor)

scene.caption = "Simulation Properties"
wtext(text=f'                                                                          Flip Counter: {flips}\n\n')

scene.append_to_caption('Select applied torque\n')
Tapp_slider = slider(id='Tapp_slider', bind=setSliders, min=0, value=Tapp, max=15, step=0.1, )
Tapp_label = wtext(text='{:.2f}\n\n'.format(Tapp_slider.value))

scene.append_to_caption('Select amount of ice\n')
ice_slider = slider(id='ice_slider', bind=setSliders, min=0, value=percent_ice, max=1, step=0.01)
ice_label = wtext(text='{:.2f}\n\n'.format(ice_slider.value))

scene.append_to_caption('Select height of release\n')
height_slider = slider(id='height_slider', bind=setSliders, min=0, value=init_height, max=5, step=0.1)
height_label = wtext(text='{:.2f}\n\n'.format(height_slider.value))

# graphs
x_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("X Position"), align='left')
xDots=gdots(color=color.red, graph=x_t)

y_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("Y Position"), align='left')
yDots=gdots(color=color.red, graph=y_t)

ak_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("Angular KE"), align='left')
akDots=gdots(color=color.green, graph=ak_t)

tk_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("Translational KE"), align='left')
tkDots=gdots(color=color.green, graph=tk_t)
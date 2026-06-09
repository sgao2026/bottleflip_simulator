Web VPython 3.2

first = vec(1,0,0)
second = vec(0,1,0)
third = vec(0,0,1)

bottom_right_back = 0
bottom_right_front = 1
bottom_left_back = 2
bottom_left_front = 3
top_right_back = 4
top_right_front = 5
top_left_back = 6
top_left_front = 7

bottle_mass = 10 # g
bottle_radius = 3.175 # cm
bottle_length = 20.3 # cm
ice_density = 0.917 # g/cm^3

g = -1000 # cm/s^2

scene.width = 700
scene.height = 500
scene.userzoom = False
scene.camera.pos = vec(0,bottle_length * 2,100)

t = 0.00
dt = 0.005
flips = 0
trail = []

Fapp = vec(-4163000,0,0) # user determined torque applied
percent_ice = 0.5 # percentage of total volume of the bottle
init_pos = vec(40,0,0) # coordinate of bottle
release_angle = pi/2

wrist = sphere(pos=init_pos + vec(0,bottle_length + 7,0), radius = 0.5)
origin = sphere(color=color.yellow)

def orth(u): # rotate pi/2 ccw
    return cross(u, -1 * third)

def vol(shape): # cylinders only
    return pi * shape.radius**2 * shape.length

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def torque (lever_arm, force):
    return cross(lever_arm, force)

def com_ind(shape):
    return shape.pos + hat(shape.axis) * shape.length * 0.5
    
def com_pts (mass, pos):
    weighted = vec(0,0,0)
    for i in range(mass.length):
        weighted = weighted + mass[i]*pos[i]
    return weighted / sum(mass)

## draw bottle
bottle_ice = group()

bottle = cylinder(radius=bottle_radius, length=bottle_length, color=color.white, opacity=0.5, group=bottle_ice)
bottle_com = sphere(pos=com_ind(bottle), visible=False, group=bottle_ice)

ice = cylinder(pos=bottle.pos, radius=bottle.radius, length=percent_ice * bottle.length, color=color.cyan, opacity=0.5, group=bottle_ice)
ice_mass = vol(ice) * ice_density
ice_com = sphere(pos=com_ind(ice), visible=False, group=bottle_ice)

bottle_ice_com_pos = com_pts((bottle_mass, ice_mass), (bottle_ice.group_to_world(bottle_com.pos), bottle_ice.group_to_world(ice_com.pos)))

bottle.pos = bottle.pos - bottle_ice_com_pos
bottle_com.pos = bottle_com.pos - bottle_ice_com_pos
ice.pos = ice.pos - bottle_ice_com_pos
ice_com.pos = ice_com.pos - bottle_ice_com_pos

bottle_ice_com = sphere(color=color.red, make_trail=False, group=bottle_ice)

bottle_ice.tvel = vec(0,0,0)
bottle_ice.avel = 0
bottle_ice.theta = 0

Farrow = arrow(pos=bottle_ice.world_to_group(bottle.pos + first * bottle.length), axis=hat(orth(bottle_ice.axis))*mag(Fapp)*10**-5, shaftwidth=1, color=color.red, group=bottle_ice)
bottle_ice.rotate(axis=third, angle=pi/2)
bottle_ice_com_pos = rotate(bottle_ice_com_pos, axis=third, angle=pi/2)
bottle_ice.pos = init_pos - bottle.pos

init_axis = bottle_ice.axis
init_tvel = bottle_ice.tvel
init_avel = bottle_ice.avel
init_theta = bottle_ice.theta

# win/lose screen
win = text(pos=vec(-50,50,0), height=10, text='Success!', align='center', color=color.green, visible=False)
lose = text(pos=vec(-50,50,0), height=10, text='Fail!', align='center', color=color.red, visible=False)

def get_contact_points():
    result = []
    for v in bottle.bounding_box():
        v = bottle_ice.group_to_world(v)
        if dot(v, second) <= 0: result.append(v)
    return result

def full_contact(ground):
    contact_count = 0
    
    for v in bottle.bounding_box():
        v = bottle_ice.group_to_world(v)
        if dot(v, second) <= ground: contact_count = contact_count + 1
    
    return contact_count == 4

def check_upright():
    print(dot(hat(bottle_ice.axis), second))
    return isclose(abs(dot(hat(bottle_ice.axis), second)), 1, abs_tol=0.0001)

def setup():
    global bottle_ice, flips, t, win
    
    # reset everything
    bottle_ice.axis = init_axis
    bottle_ice.pos = init_pos - bottle.pos
    bottle_ice.tvel = init_tvel
    bottle_ice.avel = init_avel
    bottle_ice.theta = init_theta
    flips = 0
    t = 0
    
    # clear trail
    for p in trail:
        p.visible = False
        p = None
    trail.clear()
    
    # hide win screen
    win.visible = False
    lose.visible = False
    
def draw_parabola (v_initial,  a_y = g):
    global t, bottle_ice, bottle_ice_com, flips
    v_x = dot(v_initial, first)
    v_y = dot(v_initial, second)
    
    x = dot(bottle_ice.group_to_world(bottle.pos), first)
    y = dot(bottle_ice.group_to_world(bottle.pos), second)
    
    d_theta = 0
    while len(get_contact_points()) == 0:
        rate(1 / dt)
        # rotate
        bottle_ice.rotate(axis=-1*third, angle=bottle_ice.avel * dt, origin=bottle_ice.pos)
        d_theta = d_theta + bottle_ice.avel * dt
        if d_theta > 2*pi:
            d_theta = d_theta % 2*pi
            flips = flips + 1
            flips_label.text = f'Flip Counter: {flips}'
        
        d_x = v_x * dt
        
        v_y = v_y + a_y * dt
        d_y = v_y * dt
        y = y + d_y
        
        bottle_ice.pos = bottle_ice.pos + vec(d_x,d_y,0)
        
        xDots.plot(t,x)
        yDots.plot(t,y)
        tkDots.plot(t, 0.5 * (ice_mass + bottle_mass) * (v_x**2 + v_y**2))        
        
        t = t + dt
        
        # trail
        trail.append(sphere(pos=bottle_ice.pos, color=ice.color))    bottle_ice_com.make_trail = False
    return

def flip():
    global t, bottle_ice
        
    F_g = (ice_mass + bottle_mass) * vec(0,g,0)
        
    lever_app = bottle_ice.group_to_world(bottle.pos + vec(0,bottle.length,0)) - wrist.pos
        
    T_app = torque(lever_app, Fapp)
    if T_app == 0: return # not force applied
    
    I_bottle = 0.5 * bottle_mass * bottle_radius**2 + 1/12 * bottle_mass * bottle_length**2 + bottle_mass * mag(bottle_ice.group_to_world(bottle_com.pos) - wrist.pos)**2
    I_ice = 0.25 * ice_mass * ice.radius**2 + 1/12 * ice_mass * ice.length**2 + ice_mass * mag(bottle_ice.group_to_world(ice_com.pos) - wrist.pos)**2
    
    while bottle_ice.theta <= release_angle:
        rate(1 / dt)
        
        lever_g = bottle_ice.group_to_world(bottle_ice_com.pos) - wrist.pos
        T_g = torque(lever_g, F_g)
        a_a = (T_app + T_g) / (I_bottle + I_ice)
        
        bottle_ice.avel = bottle_ice.avel + mag(a_a) * dt
        bottle_ice.tvel = rotate(norm(-1 * lever_g), angle=pi/2, origin=wrist.pos) * bottle_ice.avel * mag(lever_g)
        d_theta = bottle_ice.avel * dt
        
#        arrow(pos=bottle_ice.pos, axis=10*bottle_ice.axis)
        bottle_ice.axis = rotate(bottle_ice.axis, axis=hat(a_a), angle=d_theta, origin=wrist.pos)
        bottle_ice.pos = wrist.pos + rotate(lever_g, axis=hat(a_a), angle=d_theta)
#        sphere(pos=bottle_ice.pos, color=color.purple)
        bottle_ice.theta = bottle_ice.theta + d_theta
        
        akDots.plot(t, 0.5 * (I_bottle + I_ice) * bottle_ice.avel**2)
        
        t = t + dt
        
        # trail
        trail.append(sphere(pos=bottle_ice.pos, color=ice.color))

def impact():
    global t, bottle_ice
    contact_list = get_contact_points()
    dampen = 0.9
    
    min_pos = contact_list[0]
    for v in contact_list:
        if dot(v, second) < dot(min_pos, second): min_pos = v
    min_pos = vec(dot(min_pos, first), dot(min_pos, second), 0)    
        
    F_g = (ice_mass + bottle_mass) * vec(0,g,0)
        
    I_bottle = 0.5 * bottle_mass * bottle_radius**2 + 1/12 * bottle_mass * bottle_length**2 + bottle_mass * mag(bottle_ice.group_to_world(bottle_com.pos) - min_pos)**2
    I_ice = 0.25 * ice_mass * ice.radius**2 + 1/12 * ice_mass * ice.length**2 + ice_mass * mag(bottle_ice.group_to_world(ice_com.pos) - min_pos)**2
    
    while (not full_contact(dot(min_pos, second))):
        rate(1 / dt)
        
        lever_g = bottle_ice.group_to_world(bottle_ice_com.pos) - min_pos
        T_g = torque(lever_g, F_g)
        a_a = T_g / (I_bottle + I_ice)
        
        bottle_ice.avel = (bottle_ice.avel + mag(a_a) * dt) * dampen
        bottle_ice.tvel = rotate(norm(-1 * lever_g), angle=pi/2, origin=min_pos) * bottle_ice.avel * mag(lever_g)
        d_theta = bottle_ice.avel * dt
        
#        arrow(pos=bottle_ice.pos, axis=10*bottle_ice.axis)
        bottle_ice.axis = rotate(bottle_ice.axis, axis=hat(a_a), angle=d_theta, origin=min_pos)
        bottle_ice.pos = min_pos + rotate(lever_g, axis=hat(a_a), angle=d_theta)
#        sphere(pos=bottle_ice.pos, color=color.purple)
        bottle_ice.theta = bottle_ice.theta + d_theta
        
        akDots.plot(t, 0.5 * (I_bottle + I_ice) * bottle_ice.avel**2)
        
        t = t + dt
        
        # trail
        trail.append(sphere(pos=bottle_ice.pos, color=ice.color))
    return
    
def go(): # runs simulation
    global bottle_ice, run, win, lose
    if (mag(Fapp) == 0): return
    run.text = 'Pause'
    
    # flip
    flip()
    
    # parabola
    draw_parabola(bottle_ice.tvel)
    
    # impact behavior
    impact()
    
    # check upright
    if (check_upright()):
        win.visible = True
    else:
        lose.visible = True
    
    run.text = 'Run'
    return

def setSliders(evt): # user inputs
    global Fapp, Farrow, percent_ice, init_height, ice, ice_com, bottle, bottle_ice, bottle_ice_com, init_pos, wrist, release_angle
    if evt.id == 'Fapp_slider':
        Fapp = vec(-1 * evt.value,0,0)
        Fapp_label.text = '{:.2f} kN\n\n'.format(Fapp_slider.value * 10**-5)
        
        if (mag(Farrow.axis) == 0):
            Farrow.axis = hat(orth(bottle_ice.axis)) * mag(Fapp)*10**-5
        else:
            Farrow.axis = hat(Farrow.axis) * mag(Fapp)*10**-5
    elif evt.id == 'ice_slider':
        percent_ice = evt.value
        ice_label.text = '{:.0f}%\n\n'.format(percent_ice * 100)
        
        ice.axis = bottle_ice.axis
        ice.length = bottle.length * percent_ice
        ice_mass = vol(ice) * ice_density
        ice_com.pos = com_ind(ice)
        bottle_ice_com_pos = com_pts((bottle_mass, ice_mass), (bottle_com.pos, ice_com.pos))

        bottle.pos = bottle.pos - bottle_ice_com_pos
        bottle_com.pos = bottle_com.pos - bottle_ice_com_pos
        ice.pos = ice.pos - bottle_ice_com_pos
        ice_com.pos = ice_com.pos - bottle_ice_com_pos
        bottle_ice.pos = bottle_ice.group_to_world(bottle_ice_com_pos)
        Farrow.pos = bottle.pos + hat(bottle_ice.axis) * bottle.length
        
    elif evt.id == 'height_slider':
        delta_h = evt.value - dot(init_pos,second)
        height_label.text = '{:.2f} cm\n\n'.format(init_height)
        
        init_pos = init_pos + vec(0,delta_h,0)
        wrist.pos = wrist.pos + vec(0,delta_h,0)
        bottle_ice.pos = bottle_ice.pos + vec(0,delta_h,0)
        
        init_height = evt.value
    elif evt.id == 'angle_slider':
        release_angle = evt.value
        angle_label.text = '{:.2f} radians\n\n'.format(angle_slider.value)#     print(str(evt.id) + " " + str(Tapp))

# sliders + labels
reset = button(bind=setup, text='Reset', pos=scene.title_anchor)
run = button(bind=go, text='Run', pos=scene.title_anchor)

scene.caption = "Simulation Properties"
wtext(text='                                                                          ')
flips_label = wtext(text=f'Flip Counter: {flips}')
wtext(text='\n\n')

scene.append_to_caption('Select applied force\n')
Fapp_slider = slider(id='Fapp_slider', bind=setSliders, min=0, value=mag(Fapp), max=5000000, step=10)
Fapp_label = wtext(text='{:.2f} kN\n\n'.format(Fapp_slider.value * 10**-5))

scene.append_to_caption('Select amount of ice\n')
ice_slider = slider(id='ice_slider', bind=setSliders, min=0, value=percent_ice, max=1, step=0.01)
ice_label = wtext(text='{:.0f}%\n\n'.format(ice_slider.value * 100))

scene.append_to_caption('Select height of release\n')
height_slider = slider(id='height_slider', bind=setSliders, min=0, value=dot(init_pos,second), max=bottle_length * 2, step=0.1)
height_label = wtext(text='{:.2f} cm\n\n'.format(height_slider.value))

scene.append_to_caption('Select angle of release\n')
angle_slider = slider(id='angle_slider', bind=setSliders, min=0, value=release_angle, max=pi/2, step=0.1)
angle_label = wtext(text='{:.2f} radians\n\n'.format(angle_slider.value))

# graphs
x_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("X Position"), align='left')
xDots=gdots(color=color.red, graph=x_t)

y_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("Y Position"), align='left')
yDots=gdots(color=color.red, graph=y_t)

ak_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("Angular KE"), align='left')
akDots=gdots(color=color.green, graph=ak_t)

tk_t = graph(width=350, height=250, xtitle=("Time"), ytitle=("Translational KE"), align='left')
tkDots=gdots(color=color.green, graph=tk_t)

setup()
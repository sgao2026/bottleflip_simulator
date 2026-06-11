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
water_density = 1 # g/cm^3

g = -1000 # cm/s^2

scene.width = 1200
scene.height = 500
scene.userzoom = False
scene.resizable = False
scene.camera.pos = vec(-0.14 * scene.width, 0.15 * scene.height,160)

t = 0.00
dt = 0.005
flips = 0
trail = []

Fapp = vec(-5000000,0,0) # user determined torque applied
dt = min(dt, 1.75 / (mag(Fapp) * 10**-4))
percent_fill = 0.1 # percentage of total volume of the bottle
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
bottle.mass = bottle_mass
bottle.r_mass = 0.5 * bottle.mass * bottle.radius**2 + 1/12 * bottle.mass * bottle.length**2
bottle.com = sphere(pos=com_ind(bottle), visible=False, group=bottle_ice)

ice = cylinder(pos=bottle.pos, radius=bottle.radius, length=percent_fill * bottle.length, color=color.cyan, opacity=0.5, group=bottle_ice)
ice.mass = vol(ice) * ice_density
ice.r_mass = 0.25 * ice.mass * ice.radius**2 + 1/12 * ice.mass * ice.length**2
ice.com = sphere(pos=com_ind(ice), visible=False, group=bottle_ice)

bottle_ice_com_pos = com_pts((bottle.mass, ice.mass), (bottle_ice.group_to_world(bottle.com.pos), bottle_ice.group_to_world(ice.com.pos)))

bottle.pos = bottle.pos - bottle_ice_com_pos
bottle.com.pos = bottle.com.pos - bottle_ice_com_pos
ice.pos = ice.pos - bottle_ice_com_pos
ice.com.pos = ice.com.pos - bottle_ice_com_pos

bottle_ice.com = sphere(color=color.red, make_trail=False, group=bottle_ice)
bottle_ice.mass = bottle.mass + ice.mass
bottle_ice.r_mass = bottle.r_mass + bottle.mass * mag(bottle.com.pos)**2 + ice.r_mass + ice.mass * mag(ice.com.pos)

bottle_ice.tvel = vec(0,0,0)
bottle_ice.avel = 0
bottle_ice.theta = 0

Farrow = arrow(pos=bottle_ice.world_to_group(bottle.pos + first * bottle.length), axis=hat(orth(bottle_ice.axis))*mag(Fapp)*10**-5, shaftwidth=1, color=color.red, group=bottle_ice)
bottle_ice.rotate(axis=third, angle=pi/2)
bottle_ice.pos = init_pos - bottle.pos

init_axis = bottle_ice.axis
init_tvel = bottle_ice.tvel
init_avel = bottle_ice.avel
init_theta = bottle_ice.theta

# win/lose screen
win = text(pos=vec(dot(scene.camera.pos, first), dot(scene.camera.pos, second), 0), height=20, text='Success!', align='center', color=color.green, visible=False)
lose = text(pos=vec(dot(scene.camera.pos, first), dot(scene.camera.pos, second), 0), height=20, text='Fail!', align='center', color=color.red, visible=False)

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
    return isclose(abs(dot(hat(bottle_ice.axis), second)), 1, rel_tol=dt, abs_tol=0.0001)

def setup():
    global bottle_ice, flips, t, win
    instructions.visible = True
    # reset everything
    bottle_ice.axis = init_axis
    bottle_ice.pos = init_pos - bottle.pos
    bottle_ice.tvel = init_tvel
    bottle_ice.avel = init_avel
    bottle_ice.theta = init_theta
    flips = 0
    t = 0
    
    #reset graphs
    xDots.delete()
    yDots.delete()
    tkDots.delete() 
    akDots.delete()
    
    # clear trail
    for p in trail:
        p.visible = False
        p = None
    trail.clear()
    
    # hide win screen
    win.visible = False
    lose.visible = False
    g_info.visible = False
    
    # allow run
    run.disabled = False
    
def draw_parabola (v_initial,  a_y = g):
    global t, bottle_ice, flips
    v_x = dot(v_initial, first)
    v_y = dot(v_initial, second)
    
    d_theta = 0
    while len(get_contact_points()) == 0:
        rate(1 / dt)
        # rotate
        bottle_ice.rotate(axis=-1 * third, angle=bottle_ice.avel * dt, origin=bottle_ice.pos)
        d_theta = d_theta + bottle_ice.avel * dt
        bottle_ice.theta = (d_theta + bottle_ice.theta) % (2 * pi)
        
        if d_theta > 2*pi:
            d_theta = d_theta % 2*pi
            flips = flips + 1
            flips_label.text = f'Flip Counter: {flips}'
        
        d_x = v_x * dt
        
        v_y = v_y + a_y * dt
        bottle_ice.tvel = vec(v_x, v_y, 0)
        
        d_y = v_y * dt
        
        bottle_ice.pos = bottle_ice.pos + vec(d_x,d_y,0)
        
        xDots.plot(t,dot(bottle_ice.pos, first))
        yDots.plot(t,dot(bottle_ice.pos, second))
        tkDots.plot(t, 0.5 * bottle_ice.mass * mag(bottle_ice.tvel)**2)
        akDots.plot(t, 0.5 * bottle_ice.r_mass * bottle_ice.avel**2)
        
        t = t + dt
        
        # trail
        trail.append(sphere(pos=bottle_ice.pos, color=ice.color))
    return

def flip():
    global t, bottle_ice, Farrow
        
    F_g = (ice.mass + bottle.mass) * vec(0,g,0)
        
    lever_app = bottle_ice.group_to_world(bottle.pos + vec(0,bottle.length,0)) - wrist.pos
        
    T_app = torque(lever_app, Fapp)
    
    I_bottle = bottle.r_mass + bottle.mass * mag(bottle_ice.group_to_world(bottle.com.pos) - wrist.pos)**2
    I_ice = ice.r_mass + ice.mass * mag(bottle_ice.group_to_world(ice.com.pos) - wrist.pos)**2
    
    while bottle_ice.theta <= release_angle:
        rate(1 / dt)
        
        lever_g = bottle_ice.pos - wrist.pos
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
        
        xDots.plot(t, dot(bottle_ice.pos, first))
        yDots.plot(t, dot(bottle_ice.pos, second))
        tkDots.plot(t, 0.5 * bottle_ice.mass * mag(bottle_ice.tvel)**2)
        akDots.plot(t, 0.5 * (I_bottle + I_ice) * bottle_ice.avel**2)
        
        t = t + dt
        
        # trail
        trail.append(sphere(pos=bottle_ice.pos, color=ice.color))
    Farrow.visible = False

def impact():
    global t, bottle_ice
    contact_list = get_contact_points()
    dampen = 0.9
    
    min_pos = contact_list[0]
    for v in contact_list:
        if dot(v, second) < dot(min_pos, second): min_pos = v
    min_pos = vec(dot(min_pos, first), dot(min_pos, second), 0)    
        
    F_g = (ice.mass + bottle.mass) * vec(0,g,0)
        
    I_bottle = bottle.r_mass + bottle.mass * mag(bottle_ice.group_to_world(bottle.com.pos) - min_pos)**2
    I_ice = ice.r_mass + ice.mass * mag(bottle_ice.group_to_world(ice.com.pos) - min_pos)**2
    
    while (not full_contact(dot(min_pos, second))):
        rate(1 / dt)
        
        lever_g = bottle_ice.pos - min_pos
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
        
        xDots.plot(t, dot(bottle_ice.pos, first))
        yDots.plot(t, dot(bottle_ice.pos, second))
        tkDots.plot(t, 0.5 * bottle_ice.mass * mag(bottle_ice.tvel)**2)
        akDots.plot(t, 0.5 * (I_bottle + I_ice) * bottle_ice.avel**2)
        
        t = t + dt
        
        # trail
        trail.append(sphere(pos=bottle_ice.pos, color=ice.color))
    return

def go(): # runs simulation
    global bottle_ice, run, win, lose
    if (mag(Fapp) == 0): return

    toggle_sliders()
    run.disabled = True
    
    instructions.visible = False
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
    
    toggle_sliders()
    g_info.visible = True
    return

def setSliders(evt): # user inputs
    global Fapp, Farrow, percent_fill, init_height, ice, bottle, bottle_ice, init_pos, wrist, release_angle, dt
    if evt.id == 'Fapp_slider':
        Fapp = vec(-1 * Fapp_slider.value,0,0)
        Fapp_label.text = '{:.2f} kN\n\n'.format(Fapp_slider.value * 10**-5)
        
        Farrow.visible = True
        if (mag(Farrow.axis) == 0):
            Farrow.axis = hat(orth(bottle_ice.axis)) * mag(Fapp)*10**-5
        else:
            Farrow.axis = hat(Farrow.axis) * mag(Fapp)*10**-5
        dt = min(dt, 2 / (mag(Fapp) * 10**-4))
    elif evt.id == 'fill_slider':
        percent_fill = fill_slider.value
        fill_label.text = '{:.0f}%\n\n'.format(fill_slider.value * 100)
        
        ice.axis = bottle_ice.axis
        ice.length = bottle.length * percent_fill
        ice.mass = vol(ice) * ice_density
        ice.r_mass = 0.25 * ice.mass * ice.radius**2 + 1/12 * ice.mass * ice.length**2
        ice.com.pos = com_ind(ice)
        bottle_ice_com_pos = com_pts((bottle.mass, ice.mass), (bottle.com.pos, ice.com.pos))

        bottle.pos = bottle.pos - bottle_ice_com_pos
        bottle.com.pos = bottle.com.pos - bottle_ice_com_pos
        ice.pos = ice.pos - bottle_ice_com_pos
        ice.com.pos = ice.com.pos - bottle_ice_com_pos
        bottle_ice.pos = bottle_ice.group_to_world(bottle_ice_com_pos)
        Farrow.pos = bottle.pos + hat(bottle_ice.axis) * bottle.length
        
    elif evt.id == 'height_slider':
        delta_h = height_slider.value - dot(init_pos,second)
        height_label.text = '{:.2f} cm\n\n'.format(height_slider.value)
        
        init_pos = init_pos + vec(0,delta_h,0)
        wrist.pos = wrist.pos + vec(0,delta_h,0)
        bottle_ice.pos = bottle_ice.pos + vec(0,delta_h,0)
        
        init_height = evt.value
    elif evt.id == 'angle_slider':
        release_angle = angle_slider.value
        angle_label.text = '{:.2f} radians\n\n'.format(angle_slider.value)

def randomizeSliders(evt):
    evt.id = 'Fapp_slider'
    Fapp_slider.value = round(random() * 500000) * 10
    setSliders(evt)
    
    evt.id = 'fill_slider'
    fill_slider.value = round(random(), 2)
    setSliders(evt)
    
    evt.id = 'height_slider'
    height_slider.value = round(random() * bottle_length * 2, 1)
    setSliders(evt)
    
    evt.id = 'angle_slider'
    angle_slider.value = round(random() * pi/2, 1)
    
    setup()

def toggle_sliders():
    # disable sliders
    Fapp_slider.disabled = not Fapp_slider.disabled
    fill_slider.disabled = not fill_slider.disabled
    height_slider.disabled = not height_slider.disabled
    angle_slider.disabled = not angle_slider.disabled
    
    # disable randomize
    randomize.disabled = not randomize.disabled

# sliders + labels
reset = button(bind=setup, text='Reset', pos=scene.title_anchor)
randomize = button(bind=randomizeSliders, text='Randomize', pos=scene.title_anchor)
run = button(bind=go, text='Run', pos=scene.title_anchor)

scene.caption = "Simulation Properties"
wtext(text='                                                                          ')
flips_label = wtext(text=f'Flip Counter: {flips}')
wtext(text='\n\n')

scene.append_to_caption('Select applied force\n')
Fapp_slider = slider(id='Fapp_slider', bind=setSliders, min=0, value=mag(Fapp), max=5000000, step=10)
Fapp_label = wtext(text='{:.2f} kN\n\n'.format(Fapp_slider.value * 10**-5))

scene.append_to_caption('Select amount filled\n')
fill_slider = slider(id='fill_slider', bind=setSliders, min=0, value=percent_fill, max=1, step=0.01)
fill_label = wtext(text='{:.0f}%\n\n'.format(fill_slider.value * 100))

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

# info
instructions = label(pos=vec(dot(scene.camera.pos, first),170,0), text='Instructions: Once you adjust your parameters \n using the sliders (or the Randomize button), \n click Run to watch your bottle flip!\n When you are done, click Reset, and repeat.', box=True, color=color.black, background=color.white)
g_info = label(pos=vec(dot(scene.camera.pos, first),170,0), text='Good! Now, take a look at the graphs below.\nYou can see the angular kinetic energy of the bottle,\nthe x position and y positions of the bottle, and the translational \nkinetic energy of the bottle during its flip.', box = True, color=color.black, background=color.white)

setup()

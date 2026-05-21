Web VPython 3.2

from vpython import *


bottle = cylinder(pos=vec(0, 0, 0), size=vec(1,1,1), axis=vec(0, 3, 0), color=color.white)

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

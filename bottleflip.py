from vpython import *

def torque (force, lever_arm):
    return cross(force, lever_arm)
def com (mass, pos):
    result = vec(0,0,0)
    for m,p in zip(mass,pos) :
        result = result + (m * p)
    return result / sum(mass);

masses = (10,20)
poses = (vector(0,1,0), vector(1,0,0))
print(com(masses, poses))

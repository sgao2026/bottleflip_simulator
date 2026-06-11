# bottleflip_simulator

Our bottleflip simulator allows the user to vary certain parameters when flipping a bottle full of ice. With the given sliders, the user can adjust the force applied to the bottle, the amount of ice that the bottle contains, the height above the table at which the bottle will be released from, and the angle from the vertical at which the bottle will be released (in radians). The red arrow extending from the top of the water bottle is a vector indicating both the magnitude and direction of the force applied to the bottle. The user can also choose to randomize these parameters at their own risk. 

Once the parameters are set, the program will launch the bottle and count the number of full rotations that it makes in the air. The number of rotations is indicated at the bottom right corner of the canvas by the "Flip Counter". The program will also track the angular kinetic energy of the bottle, the translational kinetic energy of the bottle, and the x-position and y-position of the bottle. 

The parameters for successfuly landing a bottle flip are set by the impact() function. If the center of mass of the bottle lies on the outside of either bottom corner of the bottle, the bottle will fall. If it aligns perfectly with either bottom edge of the bottle, it will fall in the direction of the angular velocity. 

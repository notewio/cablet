# cablet
Camera track the tip of a pen to use as a drawing tablet

## Setup

You will need:

* Writing utensil with a colored tip (preferably blue or green)
* Background that contrasts with the colored tip
* Webcam

Position the webcam so that as much of the colored tip is visible at all possible positions. It can also be helpful to lower the camera's exposure time (reduces motion blur).

At the top of `cablet.py`, there are variables that can be changed to fit. Change `sw` and `sh` to match your screen resolution, and change `lowerBound` and `upperBound` to match the color of your pen tip.

After running `cablet.py`, you need to calibrate:

1. press `C` once to begin the process
2. Position the pen at the top-left corner of your drawing area and press `C` again
3. Repeat step 2 for the other three points (top-right, bottom-left, bottom-right)

Finally, you can press `E` to enable output to mouse.

To exit, you can click on the X button, press `Q`, or if things really go wrong, opening Task Manager will stop the mouse output.
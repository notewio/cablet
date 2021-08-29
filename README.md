# cablet
Camera track the tip of a pen to use as a drawing tablet

## Setup

You will need:

* Writing utensil with a colored tip (preferably blue or green)
* Background that contrasts with the colored tip
* Webcam

Download either the compiled executable from [the releases page](https://github.com/notewio/cablet/releases/tag/release), or the source code (needs opencv, numpy and win32api).

Position the webcam so that as much of the colored tip is visible at all possible positions. It can also be helpful to lower the camera's exposure time (reduces motion blur).

You can change settings in `settings.ini`

* `screen_width`, `screen_height`: Your screen resolution
* `camera_index`: Which camera to use, 0 being the first camera
* `color_lower_bound`, `color_upper_bound`: If the color of a pixel is between these two colors, it will be tracked. Format: HSV, 0-179, 0-255, 0-255
* `dilate_iterations`: How much to scale down the mask, helps with reducing background interference, at the cost of reducing tracking resolution
* `contouring`: Whether or not to check for the biggest group of pixels, generally leave this on
* `interp`: How much to interpolate the cursor position (0 for off)
* `noshake`: Don't move the cursor unless it's moved this much (camera pixels)

Don't change anything in the calibration section, these are set automatically by the program.

After running the program, you need to calibrate:

1. press `C` once to begin the process
2. Position the pen at the top-left corner of your drawing area and press `C` again
3. Repeat step 2 for the other three points (top-right, bottom-left, bottom-right)

Finally, you can press `E` to enable output to mouse.

To exit, you can click on the X button, press `Q`, or if things really go wrong, opening Task Manager will stop the mouse output.

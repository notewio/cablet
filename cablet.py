import cv2
import numpy as np
import win32api
import warp
import sys
from threadedvideo import ThreadedVideo
from configparser import ConfigParser



##### Misc utility #####
calibNames = (
    "top left",
    "top right",
    "bottom left",
    "bottom right"
)
windowName = "Camera Feed"
def lerp(p1, p2, amt):
    return p1 + (p2 - p1) * amt



##### Configuration #####

config = ConfigParser()
config.read("settings.ini")

# Screen dimensions
sw = config.getint("Main", "screen_width")
sh = config.getint("Main", "screen_height")

# Color mask boundaries, in HSV: if the color of a pixel is between the lower and upper bound, it will be counted.
# Note: OpenCV uses this weird HSV scaling: 0-179, 0-255, 0-255
lowerBound = tuple([int(x) for x in config.get("Main", "color_lower_bound").split()])
upperBound = tuple([int(x) for x in config.get("Main", "color_upper_bound").split()])

# How much to smoothen out the image: higher = less interference, less accurate point tracking
DILATE_ITERATIONS = config.getint("Main", "dilate_iterations")

# Whether or not to do a largest contour check. If you've got good lighting (less interference) you can get away with just averaging all points instead.
CONTOURING = config.getboolean("Main", "contouring")

# Smooth things out through interpolation, at the cost of more input delay (0 for off, closer to 1 = less interp)
INTERP = config.getfloat("Main", "interp")

# Don't move the cursor unless the difference is this large (manhattan, camera coordinates) (0 for off)
NOSHAKE = config.getint("Main", "noshake")


# Warping
srcMat = [float(x) for x in config.get("Calibration", "source").split()]
dstMat = [0, 0,  1, 0,
          0, 1,  1, 1]
warpMat = [float(x) for x in config.get("Calibration", "warp").split()]



##### Globals #####

# Last known position of the pen, in camera coordinates
center = (0, 0)

# Current progress in the calibration process
# 0: out of calibration, > 0: the point we're waiting for
calibrationState = 0

# Current screen coordinates, for interpolation
csx, csy = 0, 0

# Mouse output enabled?
enabled = False

# Start the video feed
cap = ThreadedVideo()
vw, vh = cap.cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
cap.start()
frame = cap.read()
cv2.imshow(windowName, frame)



while True:

    ##### Tracking #####

    # Read camera
    frame = cap.read()

    # Mask everything but desired color
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowerBound, upperBound)
    # Mess with it a bit to smoothen out any small noise
    mask = cv2.erode(mask, None, iterations=DILATE_ITERATIONS)
    mask = cv2.dilate(mask, None, iterations=DILATE_ITERATIONS)

    # Find the appropriate
    if CONTOURING:
        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            c = max(contours, key=cv2.contourArea)
    else:
        # Just calculate average position of all points
        c = mask


    newpos = tuple(c[c[:, :, 1].argmax()][0])

    # Center point: less noisy but also unintuitive to use
    # M = cv2.moments(c)
    # m0 = M["m00"]
    # if m0 > 0:
    #     newpos = (int(M["m10"] / m0), int(M["m01"] / m0))

    dx, dy = newpos[0] - center[0], newpos[1] - center[1]
    if abs(dx) + abs(dy) > NOSHAKE:
        center = newpos

    wx, wy = warp.warp(warpMat, center[0]/vw, center[1]/vh) # Calculate warping
    sx, sy = int(wx*sw), int(wy*sh)                         # Scale to screen size

    # Set cursor position
    if enabled:
        if INTERP:
            csx, csy = int(lerp(csx, sx, INTERP)), int(lerp(csy, sy, INTERP))
            win32api.SetCursorPos((csx, csy))
        else:
            win32api.SetCursorPos((sx, sy))


    ##### Drawing #####

    # Mask overlay
    display = cv2.addWeighted(frame, 1, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), 1, 0)

    # Status text
    status_1 = "output {} | ".format("on" if enabled else "off")
    status_1 += "press c again for {} point".format(calibNames[calibrationState-1]) if calibrationState else "calibration done"
    status_2 = "cam: {},{} | warp: {:.2f},{:.2f} | screen: {},{}".format(
        *center,
        wx, wy,
        sx, sy,
    )
    cv2.putText(
        display, status_1,
        (10, 440),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2
    )
    cv2.putText(
        display, status_2,
        (10, 460),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2
    )

    # Draw average position
    cv2.circle(display, center, 5, (0, 0, 255), -1)

    # Draw calibration points
    for i in range(0, 8, 2):
        cv2.circle(
            display,
            (int(srcMat[i] * vw), int(srcMat[i+1] * vh)),
            5, (0, 255, 0), -1
        )

    # Draw to window
    cv2.imshow(windowName, display)

    # Process key events
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("c"):
        if calibrationState == 0:
            # (re)starting calibration, reset matrices
            srcMat = [0, 0, 1, 0, 0, 1, 1, 1]
            warpMat = warp.computeWarp(srcMat, dstMat)
            calibrationState = 1
        else:
            i = (calibrationState - 1) * 2
            srcMat[i]   = center[0] / vw
            srcMat[i+1] = center[1] / vh
            if calibrationState == 4:
                warpMat = warp.computeWarp(srcMat, dstMat)

                config.set("Calibration", "source", ' '.join(map(str, srcMat)))
                config.set("Calibration", "warp", ' '.join(map(str, warpMat)))
                with open("settings.ini", "w") as f:
                    config.write(f)

                calibrationState = 0
            else:
                calibrationState += 1
    elif key == ord("e"):
        enabled = not enabled

    # X button
    if cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.stop()
cap.cap.release()
cv2.destroyAllWindows()
sys.exit()

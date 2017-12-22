# coding: utf-8

import os
import numpy as np
import cv2
import sys
from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel

import scipy.io as sio

try:
    from pylibfreenect2 import OpenCLPacketPipeline
    pipeline = OpenCLPacketPipeline()
except:
    try:
        from pylibfreenect2 import OpenGLPacketPipeline
        pipeline = OpenGLPacketPipeline()
    except:
        from pylibfreenect2 import CpuPacketPipeline
        pipeline = CpuPacketPipeline()
print("Packet pipeline:", type(pipeline).__name__)

# Create and set logger
logger = createConsoleLogger(LoggerLevel.Debug)
setGlobalLogger(logger)

fn = Freenect2()
num_devices = fn.enumerateDevices()
if num_devices == 0:
    print("No device connected!")
    sys.exit(1)

serial = fn.getDeviceSerialNumber(0)
device = fn.openDevice(serial, pipeline=pipeline)

listener = SyncMultiFrameListener(
    FrameType.Color | FrameType.Ir | FrameType.Depth)

# Register listeners
device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()

# NOTE: must be called after device.start()
registration = Registration(device.getIrCameraParams(),
                            device.getColorCameraParams())

undistorted = Frame(512, 424, 4)
registered = Frame(512, 424, 4)

# Optinal parameters for registration
# set True if you need
need_bigdepth = True
need_color_depth_map = True
need_enable_filter = True # Filter out pixels not visible to both cameras.

bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
    if need_color_depth_map else None

framesToCapture = 1
outputDir = "output"
sceneName = "my_room"
colorDir = "images"
bigdepthDir = "bigdepth"

if not os.path.exists(outputDir):
    os.makedirs(outputDir)
    
outputDir = os.path.join(outputDir, sceneName)
if not os.path.exists(outputDir):
    os.makedirs(outputDir)  
    
colorDir = os.path.join(outputDir, colorDir)
if not os.path.exists(colorDir):
    os.makedirs(colorDir)

bigdepthDir = os.path.join(outputDir, bigdepthDir)
if not os.path.exists(bigdepthDir):
    os.makedirs(bigdepthDir)
    
for x in range(0, framesToCapture):
    frames = listener.waitForNewFrame()
    frameNum = "%04d" % (x)

    color = frames["color"]
    ir = frames["ir"]
    depth = frames["depth"]

    registration.apply(color, depth, undistorted, registered,
                       enable_filter=need_enable_filter,
                       bigdepth=bigdepth,
                       color_depth_map=color_depth_map)

    # NOTE for visualization:
    # cv2.imshow without OpenGL backend seems to be quite slow to draw all
    # things below. Try commenting out some imshow if you don't have a fast
    # visualization backend.
    cv2.imwrite(os.path.join(outputDir, "ir" + frameNum + ".png"), ir.asarray() / 65535.)
    cv2.imwrite(os.path.join(outputDir, "depth" + frameNum + ".png"), depth.asarray() / 4500.)
    
    # Convert from RGBX or BGRX to RGB or BGR
    colorArray = color.asarray()
    print(colorArray.shape)
    trimColor = np.zeros( (np.size(colorArray,0), np.size(colorArray,1), 3) )
    print(trimColor.shape)
    trimColor[:,:,0] = colorArray[:,:,0]
    trimColor[:,:,1] = colorArray[:,:,1]
    trimColor[:,:,2] = colorArray[:,:,2]
    
    cv2.imwrite(os.path.join(colorDir, "img_" + frameNum + ".png"), cv2.resize(trimColor,
                                   (int(1920 / 3), int(1080 / 3))))
    cv2.imwrite(os.path.join(outputDir, "color" + frameNum + ".png"), cv2.resize(trimColor,
                                   (int(1920 / 3), int(1080 / 3))))
    cv2.imwrite(os.path.join(outputDir, "registered" + frameNum + ".png"), registered.asarray(np.uint8))

    if need_bigdepth:
        bigdepthArray = bigdepth.asarray(np.float32) / 4500. # This is a max depth
        print(bigdepthArray.shape)
        print(bigdepthArray)
        
        #bigdepthArray = bigdepthArray.astype(np.uint16)
        cv2.imshow("bigdepth", cv2.resize(bigdepthArray,
                                          (int(1920 / 3), int(1082 / 3))))
        key = cv2.waitKey(delay=1000)
        
        #bigdepthNorm = np.zeros( (np.size(bigdepthArray)) )
        #cv2.normalize(bigdepthArray, bigdepthNorm)
        bigdepthArray[bigdepthArray == np.inf] = 1
        print(bigdepthArray)
        cv2.imwrite(os.path.join(bigdepthDir, "img_" + frameNum + ".png"), cv2.resize(bigdepthArray,
                                          (int(1920 / 3), int(1082 / 3))))
        cv2.imwrite(os.path.join(outputDir, "bigdepth" + frameNum + ".png"), cv2.resize(bigdepthArray,
                                          (int(1920 / 3), int(1082 / 3))))
        sio.savemat(os.path.join(outputDir, "bigdepth" + frameNum + ".mat"), { 'bigDepth' : bigdepthArray });
    if need_color_depth_map:
        cv2.imwrite(os.path.join(outputDir, "color_depth_map" + frameNum + ".png"), color_depth_map.reshape(424, 512))

    listener.release(frames)

    key = cv2.waitKey(delay=1)
    if key == ord('q'):
        break

device.stop()
device.close()

sys.exit(0)

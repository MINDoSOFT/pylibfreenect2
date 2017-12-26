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
#import imageio
#from skimage import io as skio 
#---------------------------
#python.exe - Entry Point Not Found
#---------------------------
#The procedure entry point mkl_aa_fw_get_workdivision could not be located in the dynamic link library C:\Users\MiNdOs\Anaconda3\envs\rgbdseg\Library\bin\mkl_intel_thread.dll. 
#---------------------------
#OK   
#---------------------------
import png

# Configuration

framesToCapture = 1000
outputDir = "output"
sceneName = "my_room"
colorDir = "images"
bigdepthDir = "bigdepth"
undistortedDir = "undistored"

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
need_color_depth_map = False

bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
    if need_color_depth_map else None

# Setup the directories
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
  
undistortedDir = os.path.join(outputDir, undistortedDir)
if not os.path.exists(undistortedDir):
    os.makedirs(undistortedDir)
  
for x in range(0, framesToCapture):
    frames = listener.waitForNewFrame()
    frameNum = "%04d" % (x)

    color = frames["color"]
    ir = frames["ir"]
    depth = frames["depth"]

    registration.apply(color, depth, undistorted, registered,
                       bigdepth=bigdepth,
                       color_depth_map=color_depth_map)

    # NOTE for visualization:
    # cv2.imshow without OpenGL backend seems to be quite slow to draw all
    # things below. Try commenting out some imshow if you don't have a fast
    # visualization backend.
    cv2.imshow("ir", ir.asarray() / 65535.)
    cv2.imshow("depth", depth.asarray() / 4500.)
    cv2.imshow("color", cv2.resize(color.asarray(),
                                   (int(1920 / 3), int(1080 / 3))))
    cv2.imshow("registered", registered.asarray(np.uint8))

    # Convert from RGBX or BGRX to RGB or BGR
    colorArray = color.asarray()
    #print(colorArray.shape)
    trimColor = np.zeros( (np.size(colorArray,0), np.size(colorArray,1), 3) )
    #print(trimColor.shape)
    trimColor[:,:,0] = colorArray[:,:,0]
    trimColor[:,:,1] = colorArray[:,:,1]
    trimColor[:,:,2] = colorArray[:,:,2]
    #skio.imsave(os.path.join(colorDir, "img_" + frameNum + ".png"), trimColor)
    
    cv2.imwrite(os.path.join(colorDir, "img_" + frameNum + ".png"), trimColor)
    
    cv2.imshow("undistored", undistorted.asarray(np.float32) / 4500.)
    #print(undistorted.asarray(np.float32) / 4500.)
    undistoredArray = undistorted.asarray(np.float32) / 4500.
    undistoredArray[undistoredArray == np.inf] = 0 # To not have Inf values, in order to allow save
    undistoredArrayAdj = np.round((undistoredArray) * 255).astype('uint8')
    
    cv2.imwrite(os.path.join(undistortedDir, "img_" + frameNum + ".png"), undistoredArrayAdj)
    
    if need_bigdepth:
        bigdepthArray = bigdepth.asarray(np.float32) / 4500. # This is a max depth
        bigdepthArray[bigdepthArray == np.inf] = 0 # To not have Inf values, in order to allow save
        print('After inf set: ')
        print(np.unique(bigdepthArray))
        bigdepthArrayAdj = np.round((bigdepthArray) * 255).astype('uint8')
        print('Adjusted big depth: ')
        print(np.unique(bigdepthArrayAdj))
        #print(np.unique(np.round((bigdepthArray) * 256)))
        cv2.imwrite(os.path.join(bigdepthDir, "img_" + frameNum + ".png"), bigdepthArrayAdj )
        cv2.imshow("bigdepth", cv2.resize(bigdepthArray,
                                          (int(1920 / 3), int(1082 / 3))))
        #cv2.imwrite(os.path.join(bigdepthDir, "img_" + frameNum + ".png"), bigdepth.asarray(np.float32) / #4500.)
        #cv2.imshow("bigdepth", cv2.resize(bigdepthArray * 256,
        #                                  (int(1920 / 3), int(1082 / 3))))
        
        
        #bigdepthArray = bigdepth.asarray(np.float32)
        #bigdepthArray[bigdepthArray == np.inf] = 4500 # To not have Inf values, in order to allow save
        #print(np.unique(bigdepthArray))
        #cv2.imwrite(os.path.join(bigdepthDir, "img_" + frameNum + ".png"), bigdepthArray)
        #cv2.imwrite(os.path.join(bigdepthDir, "img_" + frameNum + ".png"), bigdepthArray.astype('uint16'))
        
        #bigdepthNorm = np.zeros( (np.size(bigdepthArray)) )
        #cv2.normalize(bigdepthArray, bigdepthNorm)
        #bigdepthNorm = cv2.normalize(bigdepthArray, bigdepthNorm, 0, 1, cv2.NORM_MINMAX)
        #print(np.unique(bigdepthNorm))
        #cv2.imwrite(os.path.join(bigdepthDir, "img_" + frameNum + ".png"), bigdepthNorm)
        
        #im1 = np.zeros((3,3), np.uint16)
        #im1[0,0] = 1000
        #skio.imsave(os.path.join(bigdepthDir, "img111_" + frameNum + ".png"), im1, 'PNG-FI')
        #skio.imsave(os.path.join(bigdepthDir, "img111_" + frameNum + ".png"), im1)
        
        #f = open(os.path.join(bigdepthDir, "img_" + frameNum + ".png"), 'wb')      # binary mode is important
        #w = png.Writer(1920, 1082, greyscale=False, bitdepth=8)
        #w.write(f, bigdepthArray)
        #f.close()
        
    if need_color_depth_map:
        cv2.imshow("color_depth_map", color_depth_map.reshape(424, 512))

    listener.release(frames)

    key = cv2.waitKey(delay=1)
    if key == ord('q'):
        break

device.stop()
device.close()

sys.exit(0)

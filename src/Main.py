import signal
import sys
import GUI
from Misc import *



# ---------------------------------------------------------------------------------------------------------------------

def signal_Handler_SIGINT(signum: int, frame):
    print("Signal SIGINT (" + str(signum) + ") recieved ...", flush=True)
    # Do nothing ...
    #sys.exit(0)

def signal_Handler_SIGTERM(signum: int, frame):
    print("Signal SIGTERM (" + str(signum) + ") recieved ...", flush=True)
    sys.exit(0)

# =====================================================================================================================

if __name__ == "__main__":
    testPicName1: str = "" if len(sys.argv) < 2 else sys.argv[1] # "../Test_Mask.png"
    testPicName2: str = "" if len(sys.argv) < 3 else sys.argv[2] # "/home/am4/Downloads/2024_12_04__21_38__2027_Ly6G_4_rotated.tiff"
    testIm1 = None
    testIm2 = None
    picData1 = None
    picData2 = None

    # Register the signal handler
    signal.signal(signal.SIGINT, signal_Handler_SIGINT)
    signal.signal(signal.SIGTERM, signal_Handler_SIGTERM)

    if len(testPicName1) > 0:
        start("Load picture: " + testPicName1)
        testIm1 = GUI.Image.open(testPicName1)
        picData1 = np.array(testIm1).astype(np.uint8)
        end()
        print("Shape pic 1: " + str(np.array(testIm1).astype(np.uint8).shape))
    if len(testPicName2) > 0:
        start("Load picture: " + testPicName2)
        testIm2 = GUI.Image.open(testPicName2)
        picData2 = np.array(testIm2).astype(np.uint8)
        end()
        print("Shape pic 2: " + str(np.array(testIm2).astype(np.uint8).shape))

    start("Start GUI ...")
    MyGui = GUI.Gui(picData1 = picData1, picData2 = picData2, slicingFactor = 1)
    end()

    # Wird aktuell nicht verwendet
#     if len(testPicName1) > 0:
#         MyGui.set_Open_Picture_Name(testPicName1, 0)
#     if len(testPicName2) > 0:
#         MyGui.set_Open_Picture_Name(testPicName2, 1)

    # Start main loop of the GUI
    GUI.window.mainloop()

# =====================================================================================================================

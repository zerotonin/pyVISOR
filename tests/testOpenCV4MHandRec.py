# import skvideo.io
# import skvideo.datasets
# import skvideo.utils
# import skimage.io
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg

# filename = '/home/bgeurten/Desktop/smca/Vid-20171016-003.avi'

# for i in range(10):
#     print i*3
#     vid = skvideo.io.vread(filename,num_frames=i*3)
#     print vid.shape#, vid[0][0][0]
#     imgplot = plt.imshow(vid[0])
#     plt.show()


import numpy as np
import cv2

cap = cv2.VideoCapture(1)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    print ret,frame
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
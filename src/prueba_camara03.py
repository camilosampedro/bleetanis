import numpy as np
# import argparse
import cv2

camera = cv2.VideoCapture(0)
lower = np.array([85, 35, 90], dtype="uint8")
upper = np.array([140, 85, 180], dtype="uint8")
penguin_img = cv2.imread('penguin-icon-little.png', -1)
pipe_img = cv2.imread('pipe.png', -1)
flipped_pipe = cv2.flip(pipe_img, 1)
trampoline_img = cv2.imread('trampoline.png', -1)
last_x = 0
last_y = 0


def join_images(image1, image2, x, y):
    image2_height = image2.shape[0]
    image2_width = image2.shape[1]
    x = x - image2_width/2
    y = y - image2_height/2
    final_y = y+image2_height
    final_x = x+image2_width
    for c in range(0, 3):
        image1[y:final_y, x:final_x, c] = \
            image2[:, :, c] * (image2[:, :, 3]/255.0) + \
            image1[y:final_y, x: final_x, c] * \
            (1.0 - image2[:, :, 3]/255.0)
    return image1

while True:
    _, img_raw = camera.read()
    img_raw = cv2.flip(img_raw, 1)
    img = cv2.GaussianBlur(np.copy(img_raw), (5, 5), 0)
    if (last_x == 0):
        last_x = img.shape[0]/2
    if (last_y == 0):
        last_y = img.shape[1]/2

    # img = cv2.fastNlMeansDenoisingColored(img, img, 1, 10)
    # define the list of boundaries)aries
    # boundaries = [
    #     ([17, 15, 100], [155, 155, 240]),
    #     ([86, 31, 4], [220, 88, 50]),
    #     ([25, 146, 190], [62, 174, 250]),
    #     ([103, 86, 65], [145, 133, 128])
    # ]

    # for (lower, upper) in boundaries:

    mask = cv2.inRange(img, lower, upper)
    moments = cv2.moments(mask)
    # print(moments)
    area = moments['m00']
    if(area > 90000):
        # print('detected')
        x = int(moments['m10']/area)
        y = int(moments['m01']/area)
        if(abs(x-last_x) > 10 or abs(y-last_y) > 10):
            last_x = x
            last_y = y
        print("x: %s, y: %s" % (x, y))
    else:
        print('not detected')
    # Print penguin
    join_images(img_raw, penguin_img, last_x, last_y)

    # Print pipes
    join_images(img_raw, pipe_img, pipe_img.shape[1]-25, last_y)
    join_images(img_raw, flipped_pipe,
                img.shape[1]-pipe_img.shape[1]+25, last_y)

    join_images(img_raw, trampoline_img, last_x,
                img.shape[0]-pipe_img.shape[0]-30)
    output = cv2.bitwise_and(img_raw, img_raw, mask=mask)
    cv2.imshow("images", np.hstack([img_raw, output]))
    if cv2.waitKey(10) == 27:
        break

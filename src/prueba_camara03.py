import numpy as np
import cv2

# Camera source
camera = cv2.VideoCapture(0)

# Lower color recognized
lower = np.array([85, 35, 90], dtype="uint8")
# Upper color recognized
upper = np.array([140, 85, 180], dtype="uint8")

# Penguin image read from file
penguin_img = cv2.imread('penguin-icon-little.png', -1)

# Pipe image read from file
pipe_img = cv2.imread('pipe.png', -1)
# Flip pipe on x-axis
flipped_pipe = cv2.flip(pipe_img, 1)
# Trampoline image read from file
trampoline_img = cv2.imread('trampoline.png', -1)

# Initialize last_x and last_y since there isn't still a recognized object, or
# even a read image from camera
last_x = 0
last_y = 0


# Join two images. image1 must be larger than image2 and it doesn't control
# when image2 will be above image1 borders
def join_images(image1, image2, x, y):
    image2_height = image2.shape[0]
    image2_width = image2.shape[1]
    # Align to center.
    y = (y - image2_height / 2)
    x = (x - image2_width / 2)
    final_y = y + image2_height
    final_x = x + image2_width
    print("f_y: %s, f_x: %s" % (final_y, final_x))
    print("s_y: %s, s_x: %s" % (image1.shape[0], image1.shape[1]))
    for c in range(0, 3):
        image1[y:final_y, x:final_x, c] = \
            image2[:, :, c] * (image2[:, :, 3]/255.0) + \
            image1[y:final_y, x: final_x, c] * \
            (1.0 - image2[:, :, 3]/255.0)
    return image1

# Always update camera image until ESC is pressed
while True:
    # Read image
    _, img_raw = camera.read()
    # Flip image for better integration with the user.
    img_raw = cv2.flip(img_raw, 1)
    # Apply blur to remove some color noise
    img = cv2.GaussianBlur(np.copy(img_raw), (5, 5), 0)
    # Initialize last_x and last_y to center
    if (last_x == 0):
        last_x = img.shape[1]/2
    if (last_y == 0):
        last_y = img.shape[0]/2
    # img = cv2.fastNlMeansDenoisingColored(img, img, 1, 10)
    # define the list of boundaries)aries
    # boundaries = [
    #     ([17, 15, 100], [155, 155, 240]),
    #     ([86, 31, 4], [220, 88, 50]),
    #     ([25, 146, 190], [62, 174, 250]),
    #     ([103, 86, 65], [145, 133, 128])
    # ]
    # for (lower, upper) in boundaries:
    # Mask will contain areas that satisfy lower<pixel<upper
    mask = cv2.inRange(img, lower, upper)
    # Moments contain information about the mask areas
    moments = cv2.moments(mask)
    # Area will be the first moment
    area = moments['m00']
    # Check if area is big enough to be considered
    if(area > 90000):
        print('detected')
        # moments m10 and m01 will contain the found object "center"
        x = int(moments['m10']/area)
        y = int(moments['m01']/area)
        # Verify if there is a "big" movement since last checked
        if(abs(x-last_x) > 10 or abs(y-last_y) > 10):
            last_x = x
            last_y = y
        # print("x: %s, y: %s" % (x, y))
    else:
        print('not detected')
    # Always print penguin
    print("last_x: %s, last_y: %s" % (last_x, last_y))
    join_images(img_raw, penguin_img, last_x, last_y)

    # Print pipes (normal and flipped) on both sides
    join_images(img_raw, pipe_img, pipe_img.shape[1], last_y)
    join_images(img_raw, flipped_pipe,
                img.shape[1]-pipe_img.shape[1], last_y)

    # Print trampoline on the bottom
    join_images(img_raw, trampoline_img, last_x,
                img.shape[0]-pipe_img.shape[0])

    # Highlight areas found
    output = cv2.bitwise_and(img_raw, img_raw, mask=mask)

    # Show raw image with the highlighted areas
    cv2.imshow("images", np.hstack([img_raw, output]))

    # Verify if ESC key is pressed and break
    if cv2.waitKey(10) == 27:
        break

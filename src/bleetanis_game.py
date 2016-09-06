# -------------------------------------------------------------------------
# ------ BLEETANIS --------------------------------------------------------
# ------ Juego básico con cámara en OpenCV --------------------------------
# ------ Por: Camilo A. Sampedro camilo.sampedro@udea.edu.co --------------
# ------      Estudiante ingeniería de sistemas, Universidad de Antioquia -
# ------      CC 1037640884 -----------------------------------------------
# ------ Por: C. Vanessa Pérez cvanessa.perez@udea.edu.co -----------------
# ------      Estudiante ingeniería de sistemas, Universidad de Antioquia -
# ------      CC **Cédula** -----------------------------------------------
# ------ Curso Básico de Procesamiento de Imágenes y Visión Artificial ----
# ------ V1 Septiembre de 2016---------------------------------------------
# ------ Nota: Algunos comentarios se dejaron en inglés para mantener la --
# ------   aplicación legible para ambos idiomas (Inglés y español).     --
# ------ Note: Some comments were left on English to keep the            --
# ------   application readable for both English and Spanish.            --
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# - 1. Librerías necesarias -----------------------------------------------
# -   Numpy para representación de datos ----------------------------------
# -   OpenCV para procesamiento de imágenes -------------------------------
# -   Random para generar números aleatorios ------------------------------
# -------------------------------------------------------------------------
import numpy as np
import cv2
import random

# -------------------------------------------------------------------------
# - 1. Inicialización del sistema -----------------------------------------
# -------------------------------------------------------------------------

# --- Se inicializan variables globales del programa ----------------------
# ---    Camera source: De aquí se obtienen las imágenes de la cámara -----
camera = cv2.VideoCapture(0)
# ---    Lower color recognized: Este es el color mínimo a reconocer  -----
lower = np.array([85, 35, 90], dtype="uint8")
# ---    Upper color recognized: Este es el color máximo a reconocer  -----
upper = np.array([140, 85, 180], dtype="uint8")
# ---    Penguin image read from file: Leer la imagen del pingüino    -----
penguin_img = cv2.imread('penguin-icon-little.png', -1)
# ---    Pipe image read from file: Leer la imagen del tubo           -----
pipe_img = cv2.imread('pipe.png', -1)
# ---    Flip pipe on x-axis: Girar el tubo para pintarlo en la derecha ---
flipped_pipe = cv2.flip(pipe_img, 1)
# ---    Trampoline image read from file: Leer la imagen del trampolín ----
trampoline_img = cv2.imread('trampoline.png', -1)
# ---    This flag will save when there is a penguin on screen: Esta   ----
# ---       bandera dirá cuándo hay un pingüino en la pantalla (Para   ----
# ---       pintarlo de nuevo)                                         ----
no_penguin = True
# ---    last_x and last_y save the latest recognized mouse location:  ----
# ---       Estas dos variables guardan dónde se reconoció el color    ----
last_x = 0
last_y = 0

# --- User lives and points: Contador de vidas y puntos                ----
points = 0
lives = 3

# -------------------------------------------------------------------------
# - 2. Funciones del programa     -----------------------------------------
# -------------------------------------------------------------------------


# --- Join two images. image1 must be larger than image2               ----
# --- Pegar dos imágenes, image1 sobre image2. image1 debe ser más     ----
# ---    grande que image2                                             ----
def join_images(image1, image2, x, y):
    # Image dimensions
    image2_height = image2.shape[0]
    image2_width = image2.shape[1]
    image1_height = image1.shape[0]
    image1_width = image1.shape[1]
    # Align to center, x and y will be the initial coordinates
    y = (y - image2_height / 2)
    x = (x - image2_width / 2)
    # If x or why exit the larger image dimensions
    if(x < 0 or x > image1_width or y < 0 or y > image1_height):
        return
    # final_x and final_y will be the ending coordinates
    final_y = y + image2_height
    final_x = x + image2_width
    # If any of final_x or final_y exceed the image1 size, reasign that size
    # limit to that ending coordinate
    if(final_y >= image1_height):
        final_y = image1_height
    if(final_x >= image1_width):
        final_x = image1_width
    # Debugging... This could be commented
    print("f_y: %s, f_x: %s" % (final_y, final_x))
    print("s_y: %s, s_x: %s" % (image1_height, image1_width))
    # For all layers but alpha layer
    for layer in range(0, 3):
        # Insert the image2 on image1, multiplying alpha times for transparency
        image1[y:final_y, x:final_x, layer] = \
            image2[:, :, layer] * (image2[:, :, 3]/255.0) + \
            image1[y:final_y, x: final_x, layer] * \
            (1.0 - image2[:, :, 3]/255.0)
    return image1


# --- Initialize penguin coordinates (Randomize it): Inicializar las    ----
# ---   coordenadas del pinguino (De forma aleatoria).                  ----
def initialize_penguin():
    # Take global variables
    global penguin_x, penguin_y, penguin_speed_x, penguin_speed_y,\
           penguin_acceleration_y, no_penguin
    # Randomize throwing penguin from left or from right: Aleatorizar si el
    #    pinguino se tirará por la izquierda o por la derecha de la pantalla
    if(random.randint(0, 1) == 0):
        penguin_x = pipe_img.shape[1]
        penguin_speed_x = random.randint(10, 18)
    else:
        penguin_x = img.shape[1] - pipe_img.shape[1]
        penguin_speed_x = -random.randint(10, 20)
    penguin_y = 50
    penguin_acceleration_y = 1
    penguin_speed_y = 0
    no_penguin = False


# --- Update penguin coordinates on each frame: Actualizar las         ----
# ---    coordenadas del pinguino cada frame o iteración               ----
def update_penguin_coordinates():
    global penguin_x, penguin_speed_y, penguin_y
    # Update penguin_x with its respective constant speed
    penguin_x = penguin_x + penguin_speed_x
    # Before updating penguin_y, update its speed by its acceleration
    penguin_speed_y = penguin_speed_y + penguin_acceleration_y
    # Update penguin_x with its respective speed
    penguin_y = penguin_y + penguin_speed_y


# --- Detect color and if it moved enought from last checked time:     ----
# ---   Detectar los colores y si se movieron lo suficiente desde la   ----
# ---   última vez que se checkeó                                      ----
def detect_movement_of_color():
    global last_x, last_y, mask
    # Generate a mask with detected colors in range between lower and upper
    mask = cv2.inRange(img, lower, upper)
    # Moments contain information about the mask areas
    moments = cv2.moments(mask)
    # Area will be the first moment
    area = moments['m00']
    # Check if area is big enough to be considered
    if(area > 90000):
        # print('detected')
        # moments m10 and m01 will contain the found object "center"
        x = int(moments['m10']/area)
        y = int(moments['m01']/area)
        # Verify if there is a "big" movement since last checked
        if(abs(x-last_x) > 10 or abs(y-last_y) > 10):
            last_x = x
            last_y = y
        # print("x: %s, y: %s" % (x, y))
    # else:
        # print('not detected')


# -------------------------------------------------------------------------
# - 3. Lógica principal del juego     -------------------------------------
# -------------------------------------------------------------------------
# --- Always update camera image until ESC is pressed.          -----------
# --- Siempre actualizar la imagen desde la cámara hasta que se -----------
# --- presione la tecla ESC                                     -----------
# -------------------------------------------------------------------------
while True:
    # --- Read image: Leer la imagen desde la cámara                   ----
    _, img_raw = camera.read()
    # --- Flip image for better integration with the user.             ----
    # ---    Girar la imagen para que "parezca" un espejo y sea más    ----
    # ---    fácil para el usuario jugar                               ----
    img_raw = cv2.flip(img_raw, 1)
    # --- Apply blur to remove some color noise. Aplicar difuminado    ----
    # --- para que manchas de colores se desaparezcan                  ----
    img = cv2.GaussianBlur(np.copy(img_raw), (5, 5), 0)
    # --- Initialize last_x and last_y to center. Inicializar last_x y ----
    # ---    last_y para que estén en el centro de la imagen           ----
    if (last_x == 0):
        last_x = img.shape[1]/2
    if (last_y == 0):
        last_y = img.shape[0]/2

    # --- Trampoline y coordinate will be always the same              ----
    if 'trampoline_y' not in locals():
        trampoline_y = img.shape[0]-pipe_img.shape[0]

    # --- If penguin needs to be printed again from beginning          ----
    if(no_penguin):
        initialize_penguin()
    # --- Update penguin coordinates and speed every frame             ----
    update_penguin_coordinates()

    # --- Check if img has color on it                                 ----
    detect_movement_of_color()
    # --- Put lives and points on User Interface                       ----
    cv2.putText(img_raw, "(lives: %s points: %s)" % (lives, points),
                (img.shape[1] / 2 - 100, 50), cv2.FONT_HERSHEY_DUPLEX, 1, 100)
    if(penguin_y >= trampoline_y):
        if(penguin_x > last_x - trampoline_img.shape[1]/2 and
           penguin_x < last_x + trampoline_img.shape[1]/2):
            penguin_speed_y = -penguin_speed_y
            penguin_speed_x = (penguin_x - last_x)/2
        else:
            no_penguin = True
            lives = lives - 1
    if(penguin_x < pipe_img.shape[1] or penguin_x >
       img.shape[1]-pipe_img.shape[1]):
        if(penguin_y > last_y - pipe_img.shape[0] / 2 and penguin_y <
           last_y + pipe_img.shape[0] / 2):
            points = points + 500
        else:
            lives = lives - 1
        no_penguin = True
    print("last_x: %s, last_y: %s" % (last_x, last_y))
    # join_images(img_raw, penguin_img, last_x, last_y)

    # Print pipes (normal and flipped) on both sides
    join_images(img_raw, pipe_img, pipe_img.shape[1], last_y)
    join_images(img_raw, flipped_pipe,
                img.shape[1]-pipe_img.shape[1], last_y)

    # Print trampoline on the bottom
    join_images(img_raw, trampoline_img, last_x,
                trampoline_y)

    print("penguin_x: %s, penguin_y: %s" % (penguin_x, penguin_y))
    join_images(img_raw, penguin_img, penguin_x, penguin_y)

    # Highlight areas found
    output = cv2.bitwise_and(img_raw, img_raw, mask=mask)
    if(lives <= 0):
        cv2.putText(img_raw, "GAME OVER", (img.shape[1] / 2 - 100,
                    img.shape[0] / 2 - 50),
                    cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, 50)

    # Show raw image with the highlighted areas
    cv2.imshow("images", np.hstack([img_raw, output]))

    # Verify if ESC key is pressed and break
    if cv2.waitKey(10) == 27:
        break

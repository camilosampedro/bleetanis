# -----------------------------------------------------------------------------
# ------ BLEETANIS ------------------------------------------------------------
# ------ Juego básico con cámara en OpenCV ------------------------------------
# ------ Por: Camilo A. Sampedro camilo.sampedro@udea.edu.co ------------------
# ------      Estudiante ingeniería de sistemas, Universidad de Antioquia -----
# ------      CC 1037640884 ---------------------------------------------------
# ------ Por: C. Vanessa Pérez cvanessa.perez@udea.edu.co ---------------------
# ------      Estudiante ingeniería de sistemas, Universidad de Antioquia -----
# ------      CC 1128440531 ---------------------------------------------------
# ------ Curso Básico de Procesamiento de Imágenes y Visión Artificial --------
# ------ V1 Septiembre de 2016-------------------------------------------------
# ------ Nota: Algunos comentarios se dejaron en inglés para mantener la ------
# ------   aplicación legible para ambos idiomas (Inglés y español).     ------
# ------ Note: Some comments were left on English to keep the            ------
# ------   application readable for both English and Spanish.            ------
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# - 1. Librerías necesarias ---------------------------------------------------
# -   Numpy para representación de datos --------------------------------------
# -   OpenCV para procesamiento de imágenes -----------------------------------
# -   Random para generar números aleatorios ----------------------------------
# -   PyGame para reproducir sonidos ------------------------------------------
# -----------------------------------------------------------------------------
import numpy as np
import cv2
import random
import pygame


# -----------------------------------------------------------------------------
# - 1. Inicialización del sistema ---------------------------------------------
# -----------------------------------------------------------------------------
def setup():
    global camera, lower, upper, penguin_img, pipe_img, flipped_pipe, \
           trampoline_img, no_penguin, last_x, last_y, points, lives
    # --- Se inicializan variables globales del programa ----------------------
    # --- Camera source: De aquí se obtienen las imágenes de la cámara    -----
    camera = cv2.VideoCapture(0)
    # --- Music: Música      --------------------------------------------------
    pygame.init()
    pygame.mixer.music.load("song"+str(random.randint(1, 3))+".wav")
    # --- Loop forever    -----------------------------------------------------
    pygame.mixer.music.play(loops=-1)
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


# --- Join two images. base_image must be larger than top_image           ----
# --- Pegar dos imágenes, base_image sobre top_image. base_image debe ser ----
# ---    más grande que top_image                                         ----
def join_images(base_image, top_image, x, y):
    # Image dimensions
    top_image_height = top_image.shape[0]
    top_image_width = top_image.shape[1]
    base_image_height = base_image.shape[0]
    base_image_width = base_image.shape[1]
    # Align to center, x and y will be the initial coordinates
    y = (y - top_image_height / 2)
    x = (x - top_image_width / 2)
    # If x or why exit the larger image dimensions
    if(x < 10 or x > base_image_width or y < 10 or y > base_image_height):
        return
    # final_x and final_y will be the ending coordinates
    final_y = y + top_image_height
    final_x = x + top_image_width
    # If any of final_x or final_y exceed the base_image size, reasign that
    # size limit to that ending coordinate
    if(final_y >= base_image_height-10):
        final_y = base_image_height-10
    if(final_x >= base_image_width-10):
        final_x = base_image_width-10
    # Debugging... This could be commented
    # print("f_y: %s, f_x: %s" % (final_y, final_x))
    # print("s_y: %s, s_x: %s" % (base_image_height, base_image_width))
    # For all layers but alpha layer
    for layer in range(0, 3):
        # Insert the top_image on base_image, multiplying alpha times for
        # transparency
        base_image[y:final_y, x:final_x, layer] = \
            top_image[:, :, layer] * (top_image[:, :, 3]/255.0) + \
            base_image[y:final_y, x: final_x, layer] * \
            (1.0 - top_image[:, :, 3]/255.0)
    return base_image


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


# --- Check if penguin is at the bottom of the image:                  ----
# ---    Verificar si el pingüíno está en la parte inferior de la      ----
# ---    imagen                                                        ----
def check_if_penguin_has_fallen():
    global penguin_y, trampoline_y, penguin_speed_y, penguin_speed_x, \
           no_penguin, lives
    if(penguin_y >= trampoline_y):
        # --- If penguin was on trampoline zone, bounce it             ----
        # ---    Si el pingüino estaba en la zona del trampolin,       ----
        # ---    rebotar                                               ----
        if(penguin_x > last_x - trampoline_img.shape[1]/2 and
           penguin_x < last_x + trampoline_img.shape[1]/2):
            penguin_speed_y = -penguin_speed_y
            penguin_speed_x = (penguin_x - last_x)/2
        else:
            # --- Else, loose a life and reset penguin on the next     ----
            # ---    iteration                                         ----
            # --- Sino, perder una vida y reiniciar el pingüino en     ----
            # ---    la siguiente iteración                            ----
            no_penguin = True
            if lives > 0:
                lives = lives - 1


# --- Check if penguin has overpassed the image limits and apply       ----
# ---    actions when needed.                                          ----
# --- Chequear si el pinguino se salió de los límites de la imagen y   ----
# ---    aplicar las acciones que se necesiten.                        ----
def check_if_penguin_is_outside_screen():
    global points, lives, no_penguin
    if(penguin_x < pipe_img.shape[1] or penguin_x >
       img.shape[1]-pipe_img.shape[1]):
        # --- If it's on pipe zone, give points to the user            ----
        # ---    Si está por la zona de los tubos, darle puntos al     ----
        # ---    usuario                                               ----
        if(penguin_y > last_y - pipe_img.shape[0] / 2 and penguin_y <
           last_y + pipe_img.shape[0] / 2):
            points = points + 500
        else:
            # --- Else, loose a life: Sino, perder una vida            ----
            if lives > 0:
                lives = lives - 1
        # --- Anyway, reset penguin: Siempre resetear el pinguino      ----
        no_penguin = True


# --- Print all images on the last coordinates:                        ----
# ---    Pintar todas las imágenes en las coordenadas                  ----
def print_images():
    join_images(img_raw, pipe_img, pipe_img.shape[1], last_y)
    join_images(img_raw, flipped_pipe,
                img.shape[1]-pipe_img.shape[1], last_y)
    # Print trampoline on the bottom
    join_images(img_raw, trampoline_img, last_x,
                trampoline_y)
    # Debugging
    # print("penguin_x: %s, penguin_y: %s" % (penguin_x, penguin_y))
    join_images(img_raw, penguin_img, penguin_x, penguin_y)

# -------------------------------------------------------------------------
# - 3. Lógica principal del juego     -------------------------------------
# -------------------------------------------------------------------------
# --- Always update camera image until ESC is pressed.          -----------
# --- Siempre actualizar la imagen desde la cámara hasta que se -----------
# --- presione la tecla ESC                                     -----------
# -------------------------------------------------------------------------
setup()
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
                (int(img.shape[1] / 2 - 100), 50), cv2.FONT_HERSHEY_DUPLEX, 1,
                (255, 255, 255))
    # --- Check if penguin has fallen from the trampoline.             ----
    # ---    Verificar si el pingüino se cayó del trampolin            ----
    check_if_penguin_has_fallen()
    # --- Check if penguin is on x axis borders                        ----
    # ---    Verificar si el pinguino está saliéndose por los ejes de  ----
    # ---    X                                                         ----
    check_if_penguin_is_outside_screen()
    # --- Debugging, this could be commented                           ----
    # print("last_x: %s, last_y: %s" % (last_x, last_y))
    # join_images(img_raw, penguin_img, last_x, last_y)

    # Print pipes (normal and flipped) on both sides
    print_images()

    # Highlight areas found
    output = cv2.bitwise_and(img_raw, img_raw, mask=mask)
    if(lives <= 0):
        cv2.putText(img_raw, "Press <ESC> to exit",
                    (int(img.shape[1] / 2 - 150), int(img.shape[0] / 2 + 50)),
                    cv2.FONT_HERSHEY_DUPLEX, 1, (157, 15, 252))
        cv2.putText(img_raw, "GAME OVER", (int(img.shape[1] / 2 - 100),
                    int(img.shape[0] / 2 - 50)),
                    cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (255, 255, 255))

    # Show raw image with the highlighted areas
    cv2.imshow("images", np.hstack([img_raw, output]))
    # cv2.imshow("Bleetanis - Press ESC to exit - OpenCV", img_raw)

    # Verify if ESC key is pressed and break
    if cv2.waitKey(10) == 27:
        break

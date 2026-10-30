import os
import sys

import cv2
import telebot
from dotenv import load_dotenv
from PyQt5 import QtWidgets, QtGui, QtCore

from Interfaz_Proyecto_Final import Ui_MainWindow

# Environment configuration
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN was not found. Add it to the .env file."
    )

if not CHAT_ID:
    raise ValueError(
        "CHAT_ID was not found. Add it to the .env file."
    )

CHAT_ID = int(CHAT_ID)

bot = telebot.TeleBot(BOT_TOKEN)

# General configuration

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAPTURES_DIR = os.path.join(BASE_DIR, "Capturas")
SENT_IMAGES_DIR = os.path.join(BASE_DIR, "Envios")

os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(SENT_IMAGES_DIR, exist_ok=True)

# Minimum contour area required to consider that movement occurred.
MIN_CONTOUR_AREA = 1000

# Minimum time between Telegram alerts (milliseconds).
ALERT_INTERVAL = 60_000

# OpenCV -> QPixmap conversion

def convert_cv_qt(cv_img):
    """
    Convert an OpenCV BGR image into a QPixmap that can be
    displayed in the PyQt5 interface.
    """

    if len(cv_img.shape) == 2:
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
    else:
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

    height, width, channels = rgb_image.shape
    bytes_per_line = channels * width

    qt_image = QtGui.QImage(
        rgb_image.data,
        width,
        height,
        bytes_per_line,
        QtGui.QImage.Format_RGB888,
    )

    scaled_image = qt_image.scaled(
        width,
        height,
        QtCore.Qt.KeepAspectRatio,
    )

    return QtGui.QPixmap.fromImage(scaled_image)

# Main interface

class Interfaz(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the interface generated with Qt Designer.
        self.setupUi(self)

        # Disable maximize button.
        self.setWindowFlag(
            QtCore.Qt.WindowMaximizeButtonHint,
            False,
        )

        # Open the default camera.
        self.capture = cv2.VideoCapture(0)

        if not self.capture.isOpened():
            raise RuntimeError(
                "Could not open the camera."
            )

        # Previous frame used for motion detection.
        self.gray_anterior = None

        # Time of the last Telegram alert.
        self.ultima_deteccion = 0

        # Timer used to continuously obtain camera frames.
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.camara)
        self.timer.start()

    # Telegram alert

    def enviar_alerta(self, frame):
        """
        Save the detected frame and send it to Telegram.
        """

        timestamp = QtCore.QDateTime.currentDateTime().toString(
            "yyyy-MM-dd_HH-mm-ss"
        )

        filename = f"captura_{timestamp}.jpg"
        save_path = os.path.join(
            SENT_IMAGES_DIR,
            filename,
        )

        if not cv2.imwrite(save_path, frame):
            print("Could not save the alert image.")
            return

        fecha, hora = timestamp.split("_")

        try:
            with open(save_path, "rb") as photo:
                bot.send_photo(
                    CHAT_ID,
                    photo,
                )

            bot.send_message(
                CHAT_ID,
                (
                    f"Motion detected on {fecha} "
                    f"at {hora} hrs."
                ),
            )

            print("Telegram alert sent.")

        except Exception as error:
            print(
                f"Could not send the Telegram alert: {error}"
            )

    # Camera and motion detection

    def camara(self):
        ret, frame = self.capture.read()

        if not ret:
            print("Could not capture camera frame.")
            return

        # Convert frame to grayscale.
        gray_actual = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        # Slight blur helps reduce noise and false detections.
        gray_actual = cv2.GaussianBlur(
            gray_actual,
            (21, 21),
            0,
        )

        # Store the first frame as reference.
        if self.gray_anterior is None:
            self.gray_anterior = gray_actual
            self.mostrar_frame(frame)
            return

        # Calculate difference between current and previous frame.
        diff = cv2.absdiff(
            gray_actual,
            self.gray_anterior,
        )

        # Convert differences into a binary image.
        _, thresh = cv2.threshold(
            diff,
            30,
            255,
            cv2.THRESH_BINARY,
        )

        # Dilate detected regions.
        thresh = cv2.dilate(
            thresh,
            None,
            iterations=2,
        )

        # Detect contours.
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        # Remove very small contours caused by camera noise.
        significant_contours = [
            contour
            for contour in contours
            if cv2.contourArea(contour) >= MIN_CONTOUR_AREA
        ]

        # Draw detected moving objects.
        for contour in significant_contours:
            x, y, width, height = cv2.boundingRect(contour)

            cv2.rectangle(
                frame,
                (x, y),
                (x + width, y + height),
                (0, 255, 0),
                2,
            )

        # Display camera image in the GUI.
        self.mostrar_frame(frame)

        # Update reference frame.
        self.gray_anterior = gray_actual

        # Check whether meaningful motion was detected.
        if significant_contours:
            print("Motion detected.")

            deteccion_actual = (
                QtCore.QDateTime.currentMSecsSinceEpoch()
            )

            # Prevent sending Telegram notifications continuously.
            if (
                deteccion_actual - self.ultima_deteccion
                >= ALERT_INTERVAL
            ):
                self.ultima_deteccion = deteccion_actual

                self.enviar_alerta(
                    frame.copy()
                )

    # Camera display

    def mostrar_frame(self, frame):
        pixmap = convert_cv_qt(frame)

        self.label.setPixmap(
            pixmap
        )
    # Manual capture

    def realizar_captura(self):
        """
        Capture and save an image manually when the interface
        capture button is pressed.
        """

        ret, frame = self.capture.read()

        if not ret:
            print("Could not capture image.")
            return

        timestamp = QtCore.QDateTime.currentDateTime().toString(
            "yyyy-MM-dd_HH-mm-ss"
        )

        filename = f"captura_{timestamp}.jpg"

        save_path = os.path.join(
            CAPTURES_DIR,
            filename,
        )

        if cv2.imwrite(save_path, frame):
            print(
                f"Image saved: {save_path}"
            )
        else:
            print(
                "Could not save the image."
            )

    # Application shutdown

    def closeEvent(self, event):
        """
        Release the camera when the application is closed.
        """

        self.timer.stop()

        if self.capture.isOpened():
            self.capture.release()

        event.accept()

# Application entry point

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = Interfaz()
    window.show()

    sys.exit(app.exec_())
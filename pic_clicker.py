import sys, uvcham
import os
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QSignalBlocker, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QCheckBox, QMessageBox, QPushButton, QComboBox, QSlider, QGroupBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QMenu, QAction, QLineEdit
import numpy as np
import cv2

class MainWidget(QWidget):
    evtCallback = pyqtSignal(int)

    @staticmethod
    def makeLayout(lbl1, sli1, val1, lbl2, sli2, val2):
        hlyt1 = QHBoxLayout()
        hlyt1.addWidget(lbl1)
        hlyt1.addStretch()
        hlyt1.addWidget(val1)
        hlyt2 = QHBoxLayout()
        hlyt2.addWidget(lbl2)
        hlyt2.addStretch()
        hlyt2.addWidget(val2)
        vlyt = QVBoxLayout()
        vlyt.addLayout(hlyt1)
        vlyt.addWidget(sli1)
        vlyt.addLayout(hlyt2)
        vlyt.addWidget(sli2)
        return vlyt

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BFL Camera Control Panel")
        self.setMinimumSize(1200, 800)
        self.hcam = None
        self.imgWidth = 0
        self.imgHeight = 0
        self.pData = None
        self.frame = 0
        self.count = 0
        self.timer = QTimer(self)

        # Layout for controls
        vlytctrl = QVBoxLayout()

        # Camera selection
        self.combo_camera = QComboBox()
        self.combo_camera.setMinimumWidth(300)
        self.btn_refresh = QPushButton("Refresh Cameras")
        self.btn_refresh.clicked.connect(self.refreshCameras)

        # Light adjustment
        self.slider_light = QSlider(Qt.Horizontal)
        self.slider_light.setRange(0, 22)
        self.slider_light.setValue(0)
        # self.slider_light.valueChanged.connect(self.onLightChange)
        # self.lbl_light = QLabel("Light: 0")

        # Flash adjustment (now only slider and QLineEdit)
        self.slider_flash = QSlider(Qt.Horizontal)
        self.slider_flash.setRange(0, 22)
        self.slider_flash.setValue(0)
        self.slider_flash.valueChanged.connect(self.onFlashChange)
        self.lbl_flash = QLabel("Flash: 0")
        self.edit_flash = QLineEdit("0")
        self.edit_flash.setFixedWidth(60)
        self.edit_flash.returnPressed.connect(self.onFlashEdit)
        hlyt_flash = QHBoxLayout()
        hlyt_flash.addWidget(self.lbl_flash)
        hlyt_flash.addWidget(self.slider_flash)
        hlyt_flash.addWidget(self.edit_flash)
        vlytctrl.addLayout(hlyt_flash)

        # Exposure controls
        gboxexp = QGroupBox("Exposure")
        self.cbox_auto = QCheckBox("Auto exposure")
        self.cbox_auto.setEnabled(False)
        self.lbl_expoTime = QLabel("0")
        self.lbl_expoGain = QLabel("0")
        self.slider_expoTime = QSlider(Qt.Horizontal)
        self.slider_expoGain = QSlider(Qt.Horizontal)
        self.slider_expoTime.setEnabled(False)
        self.slider_expoGain.setEnabled(False)
        self.cbox_auto.stateChanged.connect(self.onAutoExpo)
        self.slider_expoTime.valueChanged.connect(self.onExpoTime)
        self.slider_expoGain.valueChanged.connect(self.onExpoGain)
        vlytexp = QVBoxLayout()
        vlytexp.addWidget(self.cbox_auto)
        vlytexp.addLayout(self.makeLayout(QLabel("Time:"), self.slider_expoTime, self.lbl_expoTime, QLabel("Gain:"), self.slider_expoGain, self.lbl_expoGain))
        gboxexp.setLayout(vlytexp)

        # White balance
        self.btn_autoWB = QPushButton("White balance")
        self.btn_autoWB.setEnabled(False)
        self.btn_autoWB.clicked.connect(self.onWB)

        # Open/Close
        self.btn_open = QPushButton("Open")
        self.btn_open.clicked.connect(self.onBtnOpen)
        self.btn_snap = QPushButton("Snap")
        self.btn_snap.setEnabled(False)
        self.btn_snap.clicked.connect(self.onBtnSnap)

        # Image name
        self.lbl_name = QLabel("Image Name:")
        self.edit_name = QLineEdit()
        self.edit_name.setMinimumWidth(200)

        # Zoom controls
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setRange(5, 30)  # 0.5x to 3.0x, step 0.1
        self.slider_zoom.setValue(15)     # Default 1.5x
        self.slider_zoom.valueChanged.connect(self.onZoomChange)
        self.lbl_zoom = QLabel("Zoom: 1.5")
        self.edit_zoom = QLineEdit("1.5")
        self.edit_zoom.setFixedWidth(60)
        self.edit_zoom.returnPressed.connect(self.onZoomEdit)
        hlyt_zoom = QHBoxLayout()
        hlyt_zoom.addWidget(self.lbl_zoom)
        hlyt_zoom.addWidget(self.slider_zoom)
        hlyt_zoom.addWidget(self.edit_zoom)
        vlytctrl.addLayout(hlyt_zoom)

        # Autofocus controls
        self.btn_af_auto = QPushButton("Autofocus ON")
        self.btn_af_auto.setEnabled(False)
        self.btn_af_auto.clicked.connect(self.onAutoFocus)
        self.btn_af_off = QPushButton("Autofocus OFF")
        self.btn_af_off.setEnabled(False)
        self.btn_af_off.clicked.connect(self.onAutoFocusOff)
        vlytctrl.addWidget(self.btn_af_auto)
        vlytctrl.addWidget(self.btn_af_off)

        # Manual focus controls
        self.slider_focus = QSlider(Qt.Horizontal)
        self.slider_focus.setRange(0, 5068)  # Typical range for UVCHAM_AFPOSITION
        self.slider_focus.setValue(0)
        self.slider_focus.valueChanged.connect(self.onFocusChange)
        self.lbl_focus = QLabel("Focus: 0")
        self.edit_focus = QLineEdit("0")
        self.edit_focus.setFixedWidth(60)
        self.edit_focus.returnPressed.connect(self.onFocusEdit)
        hlyt_focus = QHBoxLayout()
        hlyt_focus.addWidget(self.lbl_focus)
        hlyt_focus.addWidget(self.slider_focus)
        hlyt_focus.addWidget(self.edit_focus)
        vlytctrl.addLayout(hlyt_focus)

        # Layouts
        vlytctrl.addWidget(self.combo_camera)
        vlytctrl.addWidget(self.btn_refresh)
        # vlytctrl.addWidget(self.lbl_light)
        # vlytctrl.addWidget(self.slider_light)
        # Removed flash buttons from layout; flash is now handled by slider and QLineEdit
        vlytctrl.addWidget(gboxexp)
        vlytctrl.addWidget(self.btn_autoWB)
        vlytctrl.addWidget(self.btn_open)
        vlytctrl.addWidget(self.btn_snap)
        vlytctrl.addWidget(self.lbl_name)
        vlytctrl.addWidget(self.edit_name)
        vlytctrl.addStretch()
        wgctrl = QWidget()
        wgctrl.setLayout(vlytctrl)

        self.lbl_frame = QLabel()
        self.lbl_video = QLabel()
        vlytshow = QVBoxLayout()
        vlytshow.addWidget(self.lbl_video, 1)
        vlytshow.addWidget(self.lbl_frame)
        wgshow = QWidget()
        wgshow.setLayout(vlytshow)

        gmain = QGridLayout()
        gmain.setColumnStretch(0, 1)
        gmain.setColumnStretch(1, 4)
        gmain.addWidget(wgctrl)
        gmain.addWidget(wgshow)
        self.setLayout(gmain)

        self.evtCallback.connect(self.onevtCallback)
        self.timer.timeout.connect(self.onTimer)
        self.refreshCameras()

    def refreshCameras(self):
        self.combo_camera.clear()
        arr = uvcham.Uvcham.enum()
        for cam in arr:
            self.combo_camera.addItem(f"{cam.displayname} ({cam.id})", cam.id)

    def onBtnOpen(self):
        if self.hcam is not None:
            self.closeCamera()
        else:
            idx = self.combo_camera.currentIndex()
            if idx < 0:
                QMessageBox.warning(self, "Warning", "No camera selected.")
                return
            cam_id = self.combo_camera.itemData(idx)
            self.openCamera(cam_id)

    # def onLightChange(self, value):
    #     self.lbl_light.setText(f"Light: {value}")
    #     if self.hcam is not None:
    #         self.hcam.put(uvcham.UVCHAM_LIGHT_ADJUSTMENT, value)

    def onFlashChange(self, value):
        self.lbl_flash.setText(f"Flash: {value}")
        self.edit_flash.setText(str(value))
        if self.hcam is not None:
            self.hcam.put(uvcham.UVCHAM_LIGHT_ADJUSTMENT, value)

    def onBtnSnap(self):
        if self.hcam is not None and self.pData is not None:
            name = self.edit_name.text().strip()
            if not name:
                name = f"pyqt{self.count+1}"
            image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
            self.count += 1
            # Create dated folder
            today = datetime.now().strftime('%Y-%m-%d')
            folder = os.path.join(os.getcwd(), today)
            if not os.path.exists(folder):
                os.makedirs(folder)
            fname = os.path.join(folder, f"{name}.jpg")
            image.save(fname)
            QMessageBox.information(self, "Saved", f"Image saved as {fname}")

    @staticmethod
    def eventCallBack(nEvent, self):
        '''callbacks come from uvcham.dll internal threads, so we use qt signal to post this event to the UI thread'''
        self.evtCallback.emit(nEvent)

    def onevtCallback(self, nEvent):
        '''this run in the UI thread'''
        if self.hcam is not None:
            if uvcham.UVCHAM_EVENT_IMAGE & nEvent != 0:
                self.onImageEvent()
            elif uvcham.UVCHAM_EVENT_ERROR & nEvent != 0:
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Generic error.")
            elif uvcham.UVCHAM_EVENT_DISCONNECT & nEvent != 0:
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Camera disconnect.")

    def onImageEvent(self):
        self.hcam.pull(self.pData) # Pull Mode
        self.frame += 1
        img = np.frombuffer(self.pData, dtype=np.uint8)
        try:
            if img.size == self.imgWidth * self.imgHeight * 3:
                image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
            elif img.size == self.imgWidth * self.imgHeight * 3 // 2:
                img = img.reshape((int(self.imgHeight * 1.5), self.imgWidth))
                img_rgb = cv2.cvtColor(img, cv2.COLOR_YUV2RGB_I420)
                image = QImage(img_rgb.data, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
            else:
                print(f'Buffer size mismatch: got {img.size}, expected {self.imgWidth*self.imgHeight*3} or {self.imgWidth*self.imgHeight*3//2}')
                return
            newimage = image.scaled(self.lbl_video.width(), self.lbl_video.height(), Qt.KeepAspectRatio, Qt.FastTransformation)
            self.lbl_video.setPixmap(QPixmap.fromImage(newimage))
        except Exception as e:
            print(f"Image decode error: {e}. Skipping corrupted frame.")

    def onAutoExpo(self, state):
        if self.hcam is not None:
            self.hcam.put(uvcham.UVCHAM_AEXPO, 1 if state else 0)
            self.slider_expoTime.setEnabled(not state)
            self.slider_expoGain.setEnabled(not state)

    def onWB(self):
        if self.hcam is not None:
            self.hcam.put(uvcham.UVCHAM_WBMODE, 3)

    def onExpoTime(self, value):
        if self.hcam is not None:
            self.lbl_expoTime.setText(str(value))
            if not self.cbox_auto.isChecked():
               self.hcam.put(uvcham.UVCHAM_EXPOTIME, value)

    def onExpoGain(self, value):
        if self.hcam is not None:
            self.lbl_expoGain.setText(str(value))
            if not self.cbox_auto.isChecked():
               self.hcam.put(uvcham.UVCHAM_AGAIN, value)

    def updateExpoTime(self):
        val = self.hcam.get(uvcham.UVCHAM_EXPOTIME)
        with QSignalBlocker(self.slider_expoTime):
            self.slider_expoTime.setValue(val)
        self.lbl_expoTime.setText(str(val))

    def updateGain(self):
        val = self.hcam.get(uvcham.UVCHAM_AGAIN)
        with QSignalBlocker(self.slider_expoGain):
            self.slider_expoGain.setValue(val)

    def onTimer(self):
        if self.hcam is not None:
            self.lbl_frame.setText(str(self.frame))

            if self.cbox_auto.isChecked():
                self.updateExpoTime()
                self.updateGain()

    def onZoomChange(self, value):
        zoom_float = value / 10.0
        self.lbl_zoom.setText(f"Zoom: {zoom_float:.1f}")
        self.edit_zoom.setText(f"{zoom_float:.1f}")
        if self.hcam is not None:
            try:
                self.hcam.put(uvcham.UVCHAM_ZOOM, int(zoom_float * 10))  # Assuming zoom is set as integer tenths
            except Exception as e:
                print(f'Failed to set zoom: {e}')

    def onZoomEdit(self):
        val = self.edit_zoom.text()
        try:
            fval = float(val)
            if 0.5 <= fval <= 3.0:
                self.slider_zoom.setValue(int(fval * 10))
                if self.hcam is not None:
                    self.hcam.put(uvcham.UVCHAM_ZOOM, int(fval * 10))
        except Exception:
            pass

    def onFocusChange(self, value):
        self.lbl_focus.setText(f"Focus: {value}")
        self.edit_focus.setText(str(value))
        if self.hcam is not None:
            try:
                self.hcam.put(uvcham.UVCHAM_AFPOSITION, value)
            except Exception as e:
                print(f'Failed to set manual focus: {e}')

    def onFocusEdit(self):
        val = self.edit_focus.text()
        try:
            ival = int(float(val))
            if 0 <= ival <= 5068:
                self.slider_focus.setValue(ival)
                if self.hcam is not None:
                    self.hcam.put(uvcham.UVCHAM_AFPOSITION, ival)
        except Exception:
            pass
    def onFlashEdit(self):
        val = self.edit_flash.text()
        try:
            ival = int(float(val))
            if 0 <= ival <= 22:
                self.slider_flash.setValue(ival)
                if self.hcam is not None:
                    self.hcam.put(uvcham.UVCHAM_LIGHT_ADJUSTMENT, ival)
        except Exception:
            pass

    def onAutoFocus(self):
        if self.hcam is not None:
            try:
                self.hcam.put(uvcham.UVCHAM_AFMODE, 1)  # 1 = auto focus
                self.btn_af_auto.setEnabled(False)
                self.btn_af_off.setEnabled(True)
                print('Autofocus ON')
            except Exception as e:
                print(f'Failed to enable autofocus: {e}')

    def onAutoFocusOff(self):
        if self.hcam is not None:
            try:
                self.hcam.put(uvcham.UVCHAM_AFMODE, 0)  # 0 = manual focus
                self.btn_af_auto.setEnabled(True)
                self.btn_af_off.setEnabled(False)
                print('Autofocus OFF')
            except Exception as e:
                print(f'Failed to disable autofocus: {e}')

    def openCamera(self, id):
        self.hcam = uvcham.Uvcham.open(id)
        if self.hcam:
            self.frame = 0
            self.hcam.put(uvcham.UVCHAM_FORMAT, 2) #Qimage use RGB byte order

            res = self.hcam.get(uvcham.UVCHAM_RES)
            self.imgWidth = self.hcam.get(uvcham.UVCHAM_WIDTH | res)
            self.imgHeight = self.hcam.get(uvcham.UVCHAM_HEIGHT | res)
            self.pData = bytes(uvcham.TDIBWIDTHBYTES(self.imgWidth * 24) * self.imgHeight)
            try:
                self.hcam.start(None, self.eventCallBack, self) # Pull Mode
            except uvcham.HRESULTException:
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Failed to start camera.")
            else:
                self.cbox_auto.setEnabled(True)
                self.btn_autoWB.setEnabled(True)
                self.btn_open.setText("Close")
                self.btn_snap.setEnabled(True)
                self.slider_flash.setEnabled(True)
                self.btn_af_auto.setEnabled(True)
                self.btn_af_off.setEnabled(True)
                self.slider_zoom.setEnabled(True)
                self.slider_focus.setEnabled(True)

                nmin, nmax, ndef = self.hcam.range(uvcham.UVCHAM_EXPOTIME)
                self.slider_expoTime.setRange(nmin, nmax)
                nmin, nmax, ndef = self.hcam.range(uvcham.UVCHAM_AGAIN)
                self.slider_expoGain.setRange(nmin, nmax)
                bAuto = self.hcam.get(uvcham.UVCHAM_AEXPO)
                self.cbox_auto.setChecked(1 == bAuto)
                self.slider_expoTime.setEnabled(1 != bAuto)
                self.slider_expoGain.setEnabled(1 != bAuto)
                self.updateExpoTime()
                self.updateGain()

                self.timer.start(1000)

    def closeCamera(self):
        if self.hcam:
            self.hcam.put(uvcham.UVCHAM_LIGHT_ADJUSTMENT, 0)  # Turn off flash when closing
            self.hcam.put(uvcham.UVCHAM_AFMODE, 0)  # Set autofocus to manual
            self.hcam.close()
        self.hcam = None
        self.pData = None
        self.btn_open.setText("Open")
        self.timer.stop()
        self.lbl_frame.clear()
        self.cbox_auto.setEnabled(False)
        self.slider_expoGain.setEnabled(False)
        self.slider_expoTime.setEnabled(False)
        self.btn_autoWB.setEnabled(False)
        self.btn_snap.setEnabled(False)
        self.slider_flash.setEnabled(False)
        self.btn_af_auto.setEnabled(False)
        self.btn_af_off.setEnabled(False)
        self.slider_zoom.setEnabled(False)
        self.slider_focus.setEnabled(False)

    def closeEvent(self, event):
        if self.hcam is not None:
            self.hcam.close()
            self.hcam = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWidget()
    mw.show()
    sys.exit(app.exec_())
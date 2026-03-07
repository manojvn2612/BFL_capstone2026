import asyncio
import websockets
import uvcham
import pythoncom
import cv2
import numpy as np
import time


class CameraStream:
    def __init__(self):
        pythoncom.CoInitialize()

        self.hcam = None
        self.imgWidth = 0
        self.imgHeight = 0
        self.pData = None

        self.open_camera()

    def open_camera(self):
        arr = uvcham.Uvcham.enum()

        if len(arr) == 0:
            print("❌ No uvcham camera detected")
            return

        print("✅ Using uvcham:", arr[0].displayname)

        self.hcam = uvcham.Uvcham.open(arr[0].id)

        res = self.hcam.get(uvcham.UVCHAM_RES)

        self.imgWidth = self.hcam.get(uvcham.UVCHAM_WIDTH | res)
        self.imgHeight = self.hcam.get(uvcham.UVCHAM_HEIGHT | res)

        self.pData = bytearray(
            uvcham.TDIBWIDTHBYTES(self.imgWidth * 24) * self.imgHeight
        )

        self.hcam.start(None, self.camera_callback, self)

        # Flash ON (adjust 0–100)
        self.hcam.put(uvcham.UVCHAM_LIGHT_ADJUSTMENT, 80)
        
    async def stream(self, websocket, path):
        print("📡 Client connected")

        try:
            while True:
                frame = self.get_frame()

                if frame:
                    await websocket.send(frame)

                await asyncio.sleep(0.03)

        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")

    def camera_callback(self, nEvent, ctx):
        if nEvent == uvcham.UVCHAM_EVENT_IMAGE:
            try:
                self.hcam.pull(self.pData)
                self.count += 1
                print("Frame count:", self.count)
            except:
                pass

    def get_frame(self):
        if self.pData is None:
            return None

        try:
            frame = np.frombuffer(self.pData, dtype=np.uint8)

            if frame.size != self.imgWidth * self.imgHeight * 3:
                print("⚠️ Frame size mismatch")
                return None

            frame = frame.reshape((self.imgHeight, self.imgWidth, 3))

            ret, encoded = cv2.imencode(".jpg", frame)
            if not ret:
                print("⚠️ Encoding failed")
                return None

            return encoded.tobytes()

        except Exception as e:
            print("❌ Frame error:", e)
            return None


# Global camera instance
camera_stream = CameraStream()


async def start_server():
    print("🚀 WebSocket server started on ws://localhost:8765")
    async with websockets.serve(camera_stream.stream, "localhost", 8765):
        await asyncio.Future()


def get_image():
    frame = camera_stream.get_frame()
    if frame:
        return np.frombuffer(frame, dtype=np.uint8)
    return None
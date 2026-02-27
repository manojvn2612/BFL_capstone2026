# BFL Capstone 2026
Vehicle Damage Detection System

## Overview

This project is a full-stack vehicle damage detection system developed for BFL Capstone 2026.

The system consists of:

- Backend: Mask R-CNN based damage segmentation (Python)
- Frontend: React + TypeScript application
- WebSocket-based communication
- Camera capture and result visualization

---

## Project Structure

BFL_capstone2026/

Backend/
- Mask_RCNN-master/
  - backend.py
  - prediction.py
  - websocket.py
  - requirements.txt
- uvcham.py

frontend/
- src/
- package.json
- package-lock.json

.gitignore
README.md

---

# Backend Setup (Conda Environment)

## 1. Install Anaconda or Miniconda

Download and install Anaconda or Miniconda from:

https://www.anaconda.com/products/distribution

Verify installation:

conda --version

---

## 2. Create Conda Environment

Create a new environment with Python 3.8 (recommended for Mask R-CNN compatibility):

conda create -n bfl_env python=3.8

---

## 3. Activate Environment

Windows:

conda activate bfl_env

Mac/Linux:

conda activate bfl_env

Verify Python version:

python --version

---

## 4. Install Backend Dependencies

Navigate to project root and run:

pip install -r Backend/Mask_RCNN-master/requirements.txt

If additional dependencies are required:

pip install opencv-python numpy matplotlib pillow

If using WebSocket:

pip install websockets

---

## 5. Run Backend Server

From project root:

python Backend/Mask_RCNN-master/backend.py

If WebSocket server is separate:

python Backend/Mask_RCNN-master/websocket.py

Ensure the backend runs without errors before starting frontend.

---

# Frontend Setup

## 1. Install Node.js

Download and install Node.js from:

https://nodejs.org/

Verify installation:

node --version
npm --version

---

## 2. Install Frontend Dependencies

Navigate to frontend directory:

cd frontend

Install dependencies:

npm install

---

## 3. Start Frontend Development Server

npm start

The frontend will run at:

http://localhost:3000

---

# Running the Complete System

1. Activate conda environment  
2. Start backend server  
3. Start WebSocket server (if applicable)  
4. Start frontend server  
5. Open browser at http://localhost:3000  

---

# Important Notes

- Do not commit:
  - virtual environments
  - model weights (.h5 / .pth)
  - datasets
  - .dll files
  - generated images
- Ensure .gitignore is properly configured.
- Use Python 3.8 for Mask R-CNN compatibility.

---

# Tech Stack

Backend:
- Python 3.8
- Mask R-CNN
- OpenCV
- NumPy
- WebSockets

Frontend:
- React
- TypeScript
- Node.js

---

# Author

Sayli Dhuri  
BFL Capstone 2026
# Holonomic Mobile Base Teleoperation via Computer Vision

An end-to-end ROS 2 and Gazebo robotics project that enables real-time, touchless teleoperation of an omnidirectional (holonomic) mobile robot using a custom-trained vision model. By analyzing live webcam feeds, the system maps hand positions and gestures directly to robot velocity commands.

---
## Model Training

| Detail | Value |
| --- | --- |
| Model | YOLOv11n (Ultralytics) |
| Classes | `fist`, `open_hand` |
| Dataset | 155 self-collected images (laptop webcam) |
| Split | 60% train / 20% val / 20% test |
| Epochs | 72 |
| Precision | 95.8% |
| Recall | 96.4% |
| mAP50 | 97.3% |
| mAP50-95 | 87.8% |


##  Key Features
  Tailored object detection model trained to classify and track hand states:
  - `Fist` → Emergency braking
  - `open_hand` → Navigation control

##  System Architecture

### Vision Pipeline
1. Webcam captures live frames
2. Input stream is mirrored for intuitive control
3. YOLOv11 performs gesture inference
4. Bounding box center coordinates are extracted

### ROS 2 Teleoperation Node
- Normalizes hand coordinates relative to the screen center
- Applies an Exponential Moving Average (EMA) filter
- Publishes velocity commands to `/cmd_vel`

### Gazebo Simulation
The holonomic robot receives:

```bash
geometry_msgs/msg/Twist
```

and moves omnidirectionally inside Gazebo.

---

## Project Structure

```text
hand_control_bot/
├── src/
│   ├── my_robot_description/
│   │   ├── launch/
│   │   │   └── gazebo.launch.py
│   │   └── urdf/
│   │       └── robot.urdf
│   │
│   └── hand_teleop/
│       ├── hand_teleop/
│       │   └── hand_controller.py
│       ├── best.pt
│       └── setup.py
│
├── assets/demo.mp4
└── README.md
```

---

## Installation & Workspace Setup

### Prerequisites

Ensure your machine is running:

- Ubuntu
- ROS 2 Humble (or later)
- Gazebo

Install dependencies:

```bash
pip3 install ultralytics opencv-python torch

sudo apt install \
ros-${ROS_DISTRO}-gazebo-ros-pkgs \
ros-${ROS_DISTRO}-robot-state-publisher
```

---

## Build the Workspace

```bash
cd ~/hand_control_bot

rm -rf build/ install/ log/

colcon build

source install/setup.bash
```

---

##  Running the System

Always launch Gazebo before running the controller node.

---

###  Launch Gazebo Simulation

```bash
ros2 launch my_robot_description gazebo.launch.py
```

This will:
- Spawn the robot
- Launch physics simulation
- Start sensor publishers
- Initialize the holonomic drive plugin

---

###  Run the Hand Tracking Controller

Open another terminal:

```bash
cd ~/hand_control_bot

source install/setup.bash

ros2 run hand_teleop controller
```

This starts:
- Webcam capture
- YOLOv11 inference
- HUD overlay
- `/cmd_vel` teleoperation publishing

---

## 🕹️ Gesture Control Layout

| Gesture | Hand Position | Robot Action |
|---|---|---|
| ✊ **Fist** | Anywhere | Emergency Stop |
| ✋ **Palm** | Center Box | Idle / Brake |
| ✋ **Palm** | Upper Region | Move Forward |
| ✋ **Palm** | Lower Region | Move Backward |
| ✋ **Palm** | Left / Right | Strafe Sideways |
| ✋ **Palm** | Corners | Diagonal Glide |

---

## Performance Notes

### Proportional Velocity Scaling
The farther the hand moves from the screen center, the faster the robot moves.

### Portable Resource Management
The project avoids hardcoded paths and uses:

```python
ament_index_python
```

to dynamically locate package resources.

---

##  Demo Video

![Demo_video](assets/demo.gif)
---

##  Published ROS 2 Topics

| Topic | Type | Description |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Robot velocity commands |
| `/scan` | `sensor_msgs/msg/LaserScan` | 360° Lidar stream |
| `/imu` | `sensor_msgs/msg/Imu` | IMU orientation data |
| `/image_raw` | `sensor_msgs/msg/Image` | Forward-facing camera feed |

---

## Core Technologies

- ROS 2 Humble
- Gazebo
- OpenCV
- YOLOv11
- PyTorch
- Python
- URDF
- RViz2

---

## Limitations

- Tested in simulation only (Gazebo).
- Small dataset (155 images) captured from a single laptop camera, so performance may drop with different cameras, lighting, or backgrounds.
- Supports only two gestures (`fist`, `open_hand`) and one hand at a time.

---

##  Future Improvements

- Multi-hand gesture support
- Dynamic speed calibration
- Gesture-based mode switching

---

## Author Note

Developed as a robotics and computer vision integration project combining:
- Real-time AI inference
- Human-machine interaction
- ROS 2 middleware
- Autonomous systems simulation

## Author:

**Harini Sathyanarayanan**
Robotics Engineer | ROS 2 · Computer Vision · Mobile Robotics
🔗 [LinkedIn](https://www.linkedin.com/in/harini-sathyanarayanan-a01986200/)
---
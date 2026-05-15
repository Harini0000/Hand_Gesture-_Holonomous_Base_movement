import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from ultralytics import YOLO
import cv2
import os 
from ament_index_python.packages import get_package_share_directory

class HandControllerNode(Node):
    def __init__(self):
        super().__init__('hand_controller_node')
        package_share_directory = get_package_share_directory('hand_teleop')
        model_path = os.path.join(package_share_directory,'best.pt')
        self.get_logger().info(f"Loading model from: {model_path}")
        
 
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
 
        self.model = YOLO(model_path)
        
   
        self.cap = cv2.VideoCapture(0)
        self.timer = self.create_timer(0.05, self.control_loop) # 20 FPS
        
        self.get_logger().info("Hand Controller Node is LIVE. Ready for gestures.")

    def control_loop(self):
        ret, frame = self.cap.read()
        if not ret: return

        # Flip frame so it acts like a mirror 
        frame = cv2.flip(frame, 1)

        results = self.model(frame, conf=0.7, verbose=False)
        msg = Twist()

        h, w, _ = frame.shape
        cx, cy = w // 2, h // 2 + 60
        deadzone = 50 

        # --- GUI OVERLAY ---
        
        cv2.rectangle(frame, (cx-deadzone, cy-deadzone), (cx+deadzone, cy+deadzone), (255, 255, 255), 1)
        cv2.putText(frame, "IDLE ZONE", (cx-40, cy-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        
        cv2.putText(frame, "FORWARD", (cx-40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "BACKWARD", (cx-45, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "LEFT", (20, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, "RIGHT", (w-80, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        if len(results[0].boxes) > 0:
            box = results[0].boxes[0]
            label = self.model.names[int(box.cls[0])]
            
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            hand_x, hand_y = (x1 + x2) / 2, (y1 + y2) / 2

            if label == 'Fist':
                msg.linear.x, msg.linear.y = 0.0, 0.0
                color = (0, 0, 255) # Red for Stop
            else:
                color = (0, 255, 0) # Green for Move
                # Calculate Velocities
                if abs(hand_y - cy) > deadzone:
                    error_y = (hand_y - cy) / cy
                    if error_y < 0:  # Moving Hand UP 
                        msg.linear.x = -error_y * 3.0  
                    else:            # Moving Hand DOWN 
                        msg.linear.x = -error_y * 1.8  
                if abs(hand_x - cx) > deadzone:
                    msg.linear.y = -((hand_x - cx) / cx) * 2.0

            # Draw Hand Tracker
            cv2.circle(frame, (int(hand_x), int(hand_y)), 10, color, -1)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            
            # Draw a line from center to hand (The "Vector")
            cv2.line(frame, (cx, cy), (int(hand_x), int(hand_y)), color, 2)

        self.cmd_vel_pub.publish(msg)
        cv2.imshow("Holonomic Hand Controller", frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = HandControllerNode()
    rclpy.spin(node)
    node.cap.release()
    cv2.destroyAllWindows()
    rclpy.shutdown()
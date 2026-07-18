#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool   # 🔥 NEW
from cv_bridge import CvBridge

import cv2
import cv2.aruco as aruco
import numpy as np
import math


class SimpleForwardTurn(Node):
    def __init__(self):
        super().__init__('simple_forward_turn')

        # ------------------- EXISTING -------------------
        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback,
            10
        )

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # 🔥 NEW publisher for obstacle signal
        self.obstacle_pub = self.create_publisher(Bool, '/robot_obstacle', 10)

        self.forward_speed = 0.3
        self.turn_speed = 0.8
        self.front_threshold = 0.4

        # ------------------- CAMERA -------------------
        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/camera/image_raw',
            self.image_callback,
            10
        )

        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.detector = aruco.ArucoDetector(self.aruco_dict, aruco.DetectorParameters())

        # ------------------- USER INPUT -------------------
        self.target_marker = int(input(
            "\nSelect target:\n"
            "0 → Grocery\n"
            "1 → Meat\n"
            "2 → Dairy\n"
            "3 → Packaged\n"
            "Enter choice: "
        ))

        self.get_logger().info(f"Target marker set to ID: {self.target_marker}")

        # ------------------- STATE -------------------
        self.marker_detected = False
        self.turning = False
        self.stop_robot = False
        self.turn_start_time = None

        self.turn_duration = 10


    # ------------------- IMAGE CALLBACK -------------------
    def image_callback(self, msg):
        if self.turning or self.stop_robot:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        corners, ids, _ = self.detector.detectMarkers(frame)

        if ids is not None:
            for marker_id in ids.flatten():

                if marker_id == 4 or marker_id == 5:
                    self.get_logger().info(f"GLOBAL MARKER {marker_id} DETECTED → TURN")

                    self.marker_detected = True
                    self.turning = True
                    self.turn_start_time = self.get_clock().now()
                    return

                elif marker_id == 6:
                    self.get_logger().info("GLOBAL MARKER 6 DETECTED → STOP")
                    self.stop_robot = True
                    return

                elif marker_id == self.target_marker:
                    self.get_logger().info(f"TARGET MARKER {marker_id} DETECTED!")

                    self.marker_detected = True
                    self.turning = True
                    self.turn_start_time = self.get_clock().now()
                    return


    # ------------------- CLEAN -------------------
    def clean(self, data, max_range):
        return [
            max_range if (x == float('inf') or x == 0.0) else x
            for x in data
        ]


    def callback(self, msg):
        twist = Twist()
        obstacle_msg = Bool()   # 🔥 NEW

        # ---------------- STOP MODE ----------------
        if self.stop_robot:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            obstacle_msg.data = False  # 🔥 no movement but not obstacle logic
            self.obstacle_pub.publish(obstacle_msg)

            self.pub.publish(twist)
            return


        # ---------------- TURNING MODE ----------------
        if self.turning:
            now = self.get_clock().now()
            elapsed = (now - self.turn_start_time).nanoseconds / 1e9

            if elapsed < self.turn_duration:
                twist.linear.x = 0.0
                twist.angular.z = self.turn_speed
            else:
                self.get_logger().info("TURN COMPLETE")
                self.turning = False
                self.marker_detected = False

            obstacle_msg.data = False  # 🔥 turning is not obstacle
            self.obstacle_pub.publish(obstacle_msg)

            self.pub.publish(twist)
            return


        # ---------------- NAVIGATION ----------------
        ranges = msg.ranges
        front = min(self.clean(ranges[170:190], msg.range_max))

        # ---------------- WAIT INSTEAD OF TURN ----------------
        if front < self.front_threshold:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            obstacle_msg.data = True   # 🔥 KEY SIGNAL
            self.get_logger().info("Obstacle ahead → waiting...")

        else:
            twist.linear.x = self.forward_speed
            twist.angular.z = 0.0

            obstacle_msg.data = False  # 🔥 CLEAR PATH

        # 🔥 publish both
        self.obstacle_pub.publish(obstacle_msg)
        self.pub.publish(twist)


def main():
    rclpy.init()
    node = SimpleForwardTurn()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool   # 🔥 NEW
from cv_bridge import CvBridge

import cv2
import cv2.aruco as aruco
import numpy as np
import math


class SimpleForwardTurn(Node):
    def __init__(self):
        super().__init__('simple_forward_turn')

        # ------------------- EXISTING -------------------
        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback,
            10
        )

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # 🔥 NEW publisher for obstacle signal
        self.obstacle_pub = self.create_publisher(Bool, '/robot_obstacle', 10)

        self.forward_speed = 0.3
        self.turn_speed = 0.8
        self.front_threshold = 0.4

        # ------------------- CAMERA -------------------
        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/camera/image_raw',
            self.image_callback,
            10
        )

        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.detector = aruco.ArucoDetector(self.aruco_dict, aruco.DetectorParameters())

        # ------------------- USER INPUT -------------------
        self.target_marker = int(input(
            "\nSelect target:\n"
            "0 → Grocery\n"
            "1 → Meat\n"
            "2 → Dairy\n"
            "3 → Packaged\n"
            "Enter choice: "
        ))

        self.get_logger().info(f"Target marker set to ID: {self.target_marker}")

        # ------------------- STATE -------------------
        self.marker_detected = False
        self.turning = False
        self.stop_robot = False
        self.turn_start_time = None

        self.turn_duration = 10


    # ------------------- IMAGE CALLBACK -------------------
    def image_callback(self, msg):
        if self.turning or self.stop_robot:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        corners, ids, _ = self.detector.detectMarkers(frame)

        if ids is not None:
            for marker_id in ids.flatten():

                if marker_id == 4 or marker_id == 5:
                    self.get_logger().info(f"GLOBAL MARKER {marker_id} DETECTED → TURN")

                    self.marker_detected = True
                    self.turning = True
                    self.turn_start_time = self.get_clock().now()
                    return

                elif marker_id == 6:
                    self.get_logger().info("GLOBAL MARKER 6 DETECTED → STOP")
                    self.stop_robot = True
                    return

                elif marker_id == self.target_marker:
                    self.get_logger().info(f"TARGET MARKER {marker_id} DETECTED!")

                    self.marker_detected = True
                    self.turning = True
                    self.turn_start_time = self.get_clock().now()
                    return


    # ------------------- CLEAN -------------------
    def clean(self, data, max_range):
        return [
            max_range if (x == float('inf') or x == 0.0) else x
            for x in data
        ]


    def callback(self, msg):
        twist = Twist()
        obstacle_msg = Bool()   # 🔥 NEW

        # ---------------- STOP MODE ----------------
        if self.stop_robot:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            obstacle_msg.data = False  # 🔥 no movement but not obstacle logic
            self.obstacle_pub.publish(obstacle_msg)

            self.pub.publish(twist)
            return


        # ---------------- TURNING MODE ----------------
        if self.turning:
            now = self.get_clock().now()
            elapsed = (now - self.turn_start_time).nanoseconds / 1e9

            if elapsed < self.turn_duration:
                twist.linear.x = 0.0
                twist.angular.z = self.turn_speed
            else:
                self.get_logger().info("TURN COMPLETE")
                self.turning = False
                self.marker_detected = False

            obstacle_msg.data = False  # 🔥 turning is not obstacle
            self.obstacle_pub.publish(obstacle_msg)

            self.pub.publish(twist)
            return


        # ---------------- NAVIGATION ----------------
        ranges = msg.ranges
        front = min(self.clean(ranges[170:190], msg.range_max))

        # ---------------- WAIT INSTEAD OF TURN ----------------
        if front < self.front_threshold:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            obstacle_msg.data = True   # 🔥 KEY SIGNAL
            self.get_logger().info("Obstacle ahead → waiting...")

        else:
            twist.linear.x = self.forward_speed
            twist.angular.z = 0.0

            obstacle_msg.data = False  # 🔥 CLEAR PATH

        # 🔥 publish both
        self.obstacle_pub.publish(obstacle_msg)
        self.pub.publish(twist)


def main():
    rclpy.init()
    node = SimpleForwardTurn()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool   # 🔥 NEW
from cv_bridge import CvBridge

import cv2
import cv2.aruco as aruco
import numpy as np
import math


class SimpleForwardTurn(Node):
    def __init__(self):
        super().__init__('simple_forward_turn')

        # ------------------- EXISTING -------------------
        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback,
            10
        )

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # 🔥 NEW publisher for obstacle signal
        self.obstacle_pub = self.create_publisher(Bool, '/robot_obstacle', 10)

        self.forward_speed = 0.3
        self.turn_speed = 0.8
        self.front_threshold = 0.4

        # ------------------- CAMERA -------------------
        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(
            Image,
            '/camera/camera/image_raw',
            self.image_callback,
            10
        )

        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.detector = aruco.ArucoDetector(self.aruco_dict, aruco.DetectorParameters())

        # ------------------- USER INPUT -------------------
        self.target_marker = int(input(
            "\nSelect target:\n"
            "0 → Grocery\n"
            "1 → Meat\n"
            "2 → Dairy\n"
            "3 → Packaged\n"
            "Enter choice: "
        ))

        self.get_logger().info(f"Target marker set to ID: {self.target_marker}")

        # ------------------- STATE -------------------
        self.marker_detected = False
        self.turning = False
        self.stop_robot = False
        self.turn_start_time = None

        self.turn_duration = 10


    # ------------------- IMAGE CALLBACK -------------------
    def image_callback(self, msg):
        if self.turning or self.stop_robot:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        corners, ids, _ = self.detector.detectMarkers(frame)

        if ids is not None:
            for marker_id in ids.flatten():

                if marker_id == 4 or marker_id == 5:
                    self.get_logger().info(f"GLOBAL MARKER {marker_id} DETECTED → TURN")

                    self.marker_detected = True
                    self.turning = True
                    self.turn_start_time = self.get_clock().now()
                    return

                elif marker_id == 6:
                    self.get_logger().info("GLOBAL MARKER 6 DETECTED → STOP")
                    self.stop_robot = True
                    return

                elif marker_id == self.target_marker:
                    self.get_logger().info(f"TARGET MARKER {marker_id} DETECTED!")

                    self.marker_detected = True
                    self.turning = True
                    self.turn_start_time = self.get_clock().now()
                    return


    # ------------------- CLEAN -------------------
    def clean(self, data, max_range):
        return [
            max_range if (x == float('inf') or x == 0.0) else x
            for x in data
        ]


    def callback(self, msg):
        twist = Twist()
        obstacle_msg = Bool()   # 🔥 NEW

        # ---------------- STOP MODE ----------------
        if self.stop_robot:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            obstacle_msg.data = False  # 🔥 no movement but not obstacle logic
            self.obstacle_pub.publish(obstacle_msg)

            self.pub.publish(twist)
            return


        # ---------------- TURNING MODE ----------------
        if self.turning:
            now = self.get_clock().now()
            elapsed = (now - self.turn_start_time).nanoseconds / 1e9

            if elapsed < self.turn_duration:
                twist.linear.x = 0.0
                twist.angular.z = self.turn_speed
            else:
                self.get_logger().info("TURN COMPLETE")
                self.turning = False
                self.marker_detected = False

            obstacle_msg.data = False  # 🔥 turning is not obstacle
            self.obstacle_pub.publish(obstacle_msg)

            self.pub.publish(twist)
            return


        # ---------------- NAVIGATION ----------------
        ranges = msg.ranges
        front = min(self.clean(ranges[170:190], msg.range_max))

        # ---------------- WAIT INSTEAD OF TURN ----------------
        if front < self.front_threshold:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            obstacle_msg.data = True   # 🔥 KEY SIGNAL
            self.get_logger().info("Obstacle ahead → waiting...")

        else:
            twist.linear.x = self.forward_speed
            twist.angular.z = 0.0

            obstacle_msg.data = False  # 🔥 CLEAR PATH

        # 🔥 publish both
        self.obstacle_pub.publish(obstacle_msg)
        self.pub.publish(twist)


def main():
    rclpy.init()
    node = SimpleForwardTurn()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
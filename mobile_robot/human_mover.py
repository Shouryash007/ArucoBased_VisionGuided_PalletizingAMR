import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import math


class HumanMover(Node):
    def __init__(self):
        super().__init__('human_mover')

        self.dt = 0.1

        self.robot_blocked = False
        self.create_subscription(Bool, '/robot_obstacle', self.obstacle_callback, 10)

        self.humans = {
            "human_1": {
                "pub": self.create_publisher(Twist, '/human_1/cmd_vel', 10),
                "x": -2.0, "y": -12.0,
                "waypoints": [(8, -12), (-2, -12)],
                "safe_point": (-2, -12),
                "current_wp": 0,
                "wait_time": 0.0,
                "state": "NORMAL"
            },

            "human_2": {
                "pub": self.create_publisher(Twist, '/human_2/cmd_vel', 10),
                "x": 10.0, "y": 0.0,
                "waypoints": [(4, 0), (10, 0)],
                "safe_point": (3, 0),
                "current_wp": 0,
                "wait_time": 0.0,
                "state": "NORMAL"
            }
        }

        self.human3_pub = self.create_publisher(Twist, '/human_3/cmd_vel', 10)

        self.timer = self.create_timer(0.1, self.move)

    def obstacle_callback(self, msg):
        self.robot_blocked = msg.data

    def move(self):
        self.human3_pub.publish(Twist())

        for name, h in self.humans.items():

            msg = Twist()

            # ===================== GLOBAL TRIGGER =====================
            if self.robot_blocked and h["state"] == "NORMAL":
                h["state"] = "FREEZE"
                h["wait_time"] = 5.0   # 🔥 wait at same spot

            # ===================== STATE MACHINE =====================

            # FREEZE (stay exactly where they are)
            if h["state"] == "FREEZE":
                msg.linear.x = 0.0
                h["wait_time"] -= self.dt

                if h["wait_time"] <= 0:
                    h["state"] = "RETREAT"

                h["pub"].publish(msg)
                continue

            # RETREAT (go to safe point AFTER delay)
            if h["state"] == "RETREAT":

                tx, ty = h["safe_point"]
                dx = tx - h["x"]
                dy = ty - h["y"]

                speed = 0.6

                if name == "human_1":
                    if abs(dx) > 0.05:
                        step = math.copysign(min(speed * self.dt, abs(dx)), dx)
                        msg.linear.x = step / self.dt
                        h["x"] += step
                    else:
                        h["wait_time"] = 15.0
                        h["state"] = "WAIT"

                elif name == "human_2":
                    if abs(dx) > 0.05:
                        step = math.copysign(min(speed * self.dt, abs(dx)), dx)
                        msg.linear.x = step / self.dt
                        h["x"] += step
                    else:
                        h["wait_time"] = 15.0
                        h["state"] = "WAIT"

                h["pub"].publish(msg)
                continue

            # WAIT (stay at safe point)
            if h["state"] == "WAIT":
                h["wait_time"] -= self.dt
                msg.linear.x = 0.0

                if h["wait_time"] <= 0:
                    h["state"] = "NORMAL"

                h["pub"].publish(msg)
                continue

            # NORMAL movement
            target_x, target_y = h["waypoints"][h["current_wp"]]

            dx = target_x - h["x"]
            dy = target_y - h["y"]

            speed = 0.6

            if name == "human_1":
                if abs(dx) > 0.05:
                    step = math.copysign(min(speed * self.dt, abs(dx)), dx)
                    msg.linear.x = step / self.dt
                    h["x"] += step
                else:
                    h["current_wp"] = (h["current_wp"] + 1) % 2

            elif name == "human_2":
                if abs(dx) > 0.05:
                    step = math.copysign(min(speed * self.dt, abs(dx)), dx)
                    msg.linear.x = step / self.dt
                    h["x"] += step
                else:
                    h["current_wp"] = (h["current_wp"] + 1) % 2

            h["pub"].publish(msg)


def main():
    rclpy.init()
    node = HumanMover()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
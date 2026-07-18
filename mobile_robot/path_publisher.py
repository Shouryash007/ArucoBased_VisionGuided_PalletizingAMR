import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped


class PathPublisher(Node):

    def __init__(self):
        super().__init__('path_publisher')

        # Subscribe to odometry
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Publish path
        self.path_publisher = self.create_publisher(
            Path,
            '/path',
            10
        )

        # Path message
        self.path_msg = Path()
        self.path_msg.header.frame_id = 'map'

    def odom_callback(self, msg):

        pose = PoseStamped()

        pose.header = msg.header
        pose.header.frame_id = 'map'

        pose.pose = msg.pose.pose

        # Store poses
        self.path_msg.header.stamp = self.get_clock().now().to_msg()
        self.path_msg.poses.append(pose)

        # Publish path
        self.path_publisher.publish(self.path_msg)


def main(args=None):

    rclpy.init(args=args)

    node = PathPublisher()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    urdf_file = '/home/shourya007/miniprjct_ws/src/mobile_robot/urdf/robot.urdf'

    robot_description = ParameterValue(
        Command(['cat ', urdf_file]),
        value_type=str
    )

    return LaunchDescription([

        # Start Gazebo WITH world
        ExecuteProcess(
            cmd=[
                'gazebo',
                '--verbose',
                '-s', '/opt/ros/humble/lib/libgazebo_ros_init.so',
                '-s', '/opt/ros/humble/lib/libgazebo_ros_factory.so',
                '/home/shourya007/miniprjct_ws/src/mobile_robot/worlds/warehouse_scene.world'
            ],
            output='screen'
        ),

        # ✅ ROBOT STATE PUBLISHER
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }]
        ),

        # ✅ JOINT STATE PUBLISHER
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': True
            }]
        ),

        # ✅ PATH PUBLISHER NODE
        Node(
            package='mobile_robot',
            executable='path_publisher',
            name='path_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': True
            }]
        ),

        # Spawn robot + start human movement after delay
        TimerAction(
            period=5.0,
            actions=[

                Node(
                    package='gazebo_ros',
                    executable='spawn_entity.py',
                    arguments=[
                        '-entity', 'mobile_robot',
                        '-file', urdf_file,
                        '-x', '0',
                        '-y', '0',
                        '-z', '0.5'
                    ],
                    output='screen'
                ),

                Node(
                    package='mobile_robot',
                    executable='human_mover',
                    output='screen'
                )

            ]
        )
    ])
"""
order.launch.py — order_node 실행 (⑨ 말로 시키는 로봇)

    ros2 launch voice_robot_control order.launch.py

※ 로봇(또는 시뮬레이터)이 먼저 떠 있어야 합니다.
※ 어떤 작업을 어디서 할지는 order_node.py 파일 맨 위를 고쳐서 바꿉니다.
"""

from launch import LaunchDescription
from launch_ros.actions import Node

from voice_robot_control.launch_helper import config_file, moveit_config


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="voice_robot_control",
            executable="order_node",
            output="screen",
            emulate_tty=True,      # 말하고 듣는 내용이 바로바로 찍히도록
            parameters=[
                moveit_config().to_dict(),
                config_file("moveit_py.yaml"),
            ],
        )
    ])

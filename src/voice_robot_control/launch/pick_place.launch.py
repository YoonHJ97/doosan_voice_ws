"""
pick_place.launch.py — pick_place_node 실행

    ros2 launch voice_robot_control pick_place.launch.py

※ 로봇(또는 시뮬레이터)이 먼저 떠 있어야 합니다.
※ 무엇을 할지는 pick_place_node.py 파일 맨 위의 상수를 고쳐서 바꿉니다.
"""

from launch import LaunchDescription
from launch_ros.actions import Node

from voice_robot_control.launch_helper import config_file, moveit_config


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="voice_robot_control",
            executable="pick_place_node",
            output="screen",
            parameters=[
                moveit_config().to_dict(),
                config_file("moveit_py.yaml"),
            ],
        )
    ])

"""
gripper.launch.py — gripper_node 실행

    ros2 launch voice_robot_control gripper.launch.py

그리퍼만 움직이므로 MoveIt 설정이 필요 없습니다.
로봇 팔을 안 켜도 실행됩니다.

무엇을 할지는 gripper_node.py 파일 맨 위의 상수를 고쳐서 바꿉니다.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="voice_robot_control",
            executable="gripper_node",
            output="screen",
        )
    ])

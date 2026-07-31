"""
nlp.launch.py — nlp_node 실행

    ros2 launch voice_robot_control nlp.launch.py

로봇 팔이 필요 없으므로 로봇을 안 켜도 됩니다.
어떤 말을 알아들을지는 config/keyword_map.yaml 을 고칩니다.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="voice_robot_control",
            executable="nlp_node",
            output="screen",
            emulate_tty=True,
        )
    ])

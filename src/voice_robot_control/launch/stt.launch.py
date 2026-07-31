"""
stt.launch.py — stt_node 실행

    ros2 launch voice_robot_control stt.launch.py

로봇 팔이 필요 없으므로 로봇을 안 켜도 됩니다.
무엇을 바꿀지는 stt_node.py 파일 맨 위의 상수를 고칩니다.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="voice_robot_control",
            executable="stt_node",
            output="screen",
            emulate_tty=True,      # 화면에 바로바로 찍히도록
        )
    ])

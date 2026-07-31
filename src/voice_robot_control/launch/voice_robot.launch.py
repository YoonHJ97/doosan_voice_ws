"""
voice_robot.launch.py — ⑧ 음성 명령 실행 노드

    ros2 launch voice_robot_control voice_robot.launch.py

※ 로봇(또는 시뮬레이터)이 먼저 떠 있어야 합니다.
※ 말로 움직이려면 ⑥ stt_node 와 ⑦ nlp_node 도 켜야 합니다.

무엇을 할지는 voice_robot_node.py 파일 맨 위의 상수를 고칩니다.
"""

from launch import LaunchDescription
from launch_ros.actions import Node

from voice_robot_control.launch_helper import config_file, moveit_config


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="voice_robot_control",
            executable="voice_robot_node",
            output="screen",
            emulate_tty=True,
            parameters=[
                moveit_config().to_dict(),
                config_file("moveit_py.yaml"),
            ],
        )
    ])

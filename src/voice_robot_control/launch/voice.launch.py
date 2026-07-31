"""
voice.launch.py — 말로 로봇 움직이기, 한 번에 켜기

⑥ 음성 인식 + ⑦ 말→명령 + ⑧ 명령→동작 을 한 터미널에서 켠다.

    ros2 launch voice_robot_control voice.launch.py

    # 마이크 없이 (타이핑으로 시험할 때)
    ros2 launch voice_robot_control voice.launch.py use_stt:=false
    #   → 다른 터미널에서
    #      ros2 topic pub --once /stt_result std_msgs/msg/String "data: '기어 2번 집어'"

※ 로봇(또는 시뮬레이터)이 먼저 떠 있어야 합니다.

셋을 따로 켜고 싶으면 stt.launch.py / nlp.launch.py / voice_robot.launch.py
를 각각 쓰면 됩니다. 어디가 문제인지 찾을 때는 따로 켜는 쪽이 낫습니다.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from voice_robot_control.launch_helper import config_file, moveit_config


def generate_launch_description():
    args = [
        DeclareLaunchArgument(
            "use_stt", default_value="true",
            description="false 면 마이크 없이 (⑦⑧ 만 켭니다)"),
    ]

    nodes = [
        # ⑧ 명령을 받아 로봇을 움직인다 (MoveIt 필요, 15초쯤 걸림)
        Node(
            package="voice_robot_control",
            executable="voice_robot_node",
            output="screen",
            emulate_tty=True,
            parameters=[
                moveit_config().to_dict(),
                config_file("moveit_py.yaml"),
            ],
        ),

        # ⑦ 말을 명령으로 바꾼다
        Node(
            package="voice_robot_control",
            executable="nlp_node",
            output="screen",
            emulate_tty=True,
        ),

        # ⑥ 마이크로 듣는다
        Node(
            package="voice_robot_control",
            executable="stt_node",
            output="screen",
            emulate_tty=True,
            condition=IfCondition(LaunchConfiguration("use_stt")),
        ),
    ]

    안내 = LogInfo(msg=(
        "\n"
        "───────────────────────────────────────────────\n"
        "  로봇 준비에 15초쯤 걸립니다.\n"
        "  '/robot_command 를 기다립니다' 가 뜨면 말해 보세요.\n"
        "\n"
        "      \"홈으로\"  \"기어 2번 집어\"  \"전체 조립해\"  \"앞으로\"\n"
        "───────────────────────────────────────────────"))

    return LaunchDescription(args + nodes + [안내])

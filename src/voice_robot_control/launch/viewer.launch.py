"""
viewer.launch.py — 손끝 위치 보기

    ros2 launch voice_robot_control viewer.launch.py

로봇을 움직이지 않고 지금 어디 있는지만 보여줍니다.
좌표를 알아내서 다른 노드의 상수에 적어 넣을 때 씁니다.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    args = [
        DeclareLaunchArgument(
            "print_period", default_value="1.0",
            description="화면에 찍는 주기 [초], 0 이면 안 찍음"),
        DeclareLaunchArgument(
            "record_file", default_value="",
            description="저장 파일 (비우면 ~/내가_저장한_자세.yaml)"),
    ]

    node = Node(
        package="voice_robot_control",
        executable="position_viewer",
        name="position_viewer",
        output="screen",
        parameters=[{
            # print_period:=0 이 정수로 해석돼 노드가 죽는 것을 막는다
            "print_period": ParameterValue(
                LaunchConfiguration("print_period"), value_type=float),
            "record_file": ParameterValue(
                LaunchConfiguration("record_file"), value_type=str),
        }],
    )

    return LaunchDescription(args + [node])

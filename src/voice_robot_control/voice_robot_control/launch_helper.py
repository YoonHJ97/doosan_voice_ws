#!/usr/bin/env python3
"""
launch_helper.py — launch 파일들이 같이 쓰는 부분

세 개의 launch 파일(move / waypoint / gear)이 MoveIt 설정을 똑같이 만든다.
같은 내용을 세 번 적으면 한 곳만 고치고 나머지를 잊기 쉬우므로 여기 모아 둔다.
"""

from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder

PACKAGE = "voice_robot_control"


def moveit_config():
    """두산 M0609 용 MoveIt 설정을 만든다.

    planning_pipelines 와 pilz_cartesian_limits 를 빠뜨리면
    좌표로 이동할 때 "가는 길을 찾지 못했습니다" 가 뜬다.
    """
    return (
        MoveItConfigsBuilder(
            robot_name="m0609",
            package_name="dsr_moveit_config_m0609",
        )
        .robot_description()
        .robot_description_semantic()
        .robot_description_kinematics()
        .joint_limits()
        .trajectory_execution()
        .planning_scene_monitor()
        .planning_pipelines(
            default_planning_pipeline="ompl",
            pipelines=["ompl", "pilz_industrial_motion_planner"],
        )
        .pilz_cartesian_limits()
        .to_moveit_configs()
    )


def config_file(file_name: str):
    """config 폴더 안의 파일 경로."""
    return PathJoinSubstitution([FindPackageShare(PACKAGE), "config", file_name])


def 실수(argument_name):
    """launch 인자를 반드시 실수(double)로 넘긴다.

    launch 인자는 전부 글자로 들어온다. 그대로 두면 ROS 가 형을 추측하는데,
    vel_scale:=1 처럼 소수점이 없으면 정수로 판단해 버린다. 노드는 실수로
    선언해 두었으므로 형이 안 맞아 노드가 그대로 죽는다.
    """
    return ParameterValue(LaunchConfiguration(argument_name), value_type=float)


def 참거짓(argument_name):
    """launch 인자를 반드시 참/거짓(bool)으로 넘긴다."""
    return ParameterValue(LaunchConfiguration(argument_name), value_type=bool)

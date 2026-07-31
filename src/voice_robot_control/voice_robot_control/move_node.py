#!/usr/bin/env python3
"""
move_node.py — ① 단순 이동 노드  [Module-5]

로봇을 홈 자세로 보낸 다음, 정해진 좌표 한 곳으로 이동한다.
가장 기본이 되는 노드다.

    ros2 launch voice_robot_control move.launch.py

■ 실습: 아래 TARGET 의 숫자를 바꾸고 다시 실행해 보세요.
  x, y, z 의 단위는 m 입니다.  (0.5 = 50cm)
  파일을 고친 뒤 다시 빌드할 필요는 없습니다. 그냥 다시 실행하면 됩니다.
"""

import rclpy
from rclpy.logging import get_logger

from .robot_common import (
    finish, go_home, make_home_state, make_plan_params, make_pose,
    plan_and_execute, setup_robot,
)


# ══════════════════════════════════════════════════════════
#  ▼▼▼ 여기를 바꿔가며 연습하세요 ▼▼▼
# ══════════════════════════════════════════════════════════

# 어디로 갈까?  (base_link 기준, 단위 m)
TARGET = {"x": 0.500, "y": 0.000, "z": 0.500}

# 로봇 속도 (0에 가까울수록 느림. 처음에는 0.1 정도로 천천히)
SPEED = 0.15

# ══════════════════════════════════════════════════════════


def main(args=None):
    rclpy.init(args=args)
    logger = get_logger("move_node")
    logger.info("=== ① 단순 이동 시작 ===")

    robot, arm = setup_robot(logger, node_name="move_node_moveit")
    home_params, pilz_params = make_plan_params(robot, vel_move=SPEED)
    home_state = make_home_state(robot)

    # ── 1) 홈 자세로 ────────────────────────────────────
    if not go_home(robot, arm, logger, home_state, home_params):
        logger.error("홈 자세로 가지 못해 여기서 멈춥니다.")
        finish(logger)

    # ── 2) 정해둔 좌표로 ────────────────────────────────
    logger.info(
        f"=== 목표 좌표로 이동: "
        f"x={TARGET['x']:.3f}, y={TARGET['y']:.3f}, z={TARGET['z']:.3f} ==="
    )
    pose_goal = make_pose(TARGET)

    if plan_and_execute(robot, arm, logger,
                        pose_goal=pose_goal,
                        plan_parameters=pilz_params):
        logger.info("=== 도착했습니다 ===")
    else:
        logger.error("=== 목표 좌표로 가지 못했습니다 ===")

    logger.info("=== ① 단순 이동 끝 ===")
    finish(logger)


if __name__ == "__main__":
    main()

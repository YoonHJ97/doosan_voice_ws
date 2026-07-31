#!/usr/bin/env python3
"""
nlp_node.py — ⑦ 말을 명령으로 바꾸는 노드  [Module-7]

⑥ 음성 인식이 내보낸 **글자**를 받아서, 로봇이 알아들을 수 있는
**명령**으로 바꿔 준다.

    "기어 2번 집어줘"   →   pick 2
    "앞으로"            →   jog forward
    "전체 조립해"        →   pickplace all

    받는 것:  /stt_result    (⑥ 음성 인식이 보냄)
    내보내는 것: /robot_command

    ros2 launch voice_robot_control nlp.launch.py

로봇 팔이 필요 없으므로 로봇을 안 켜도 실행됩니다.

■ 실습 — 우리 팀 명령어 만들기
  config/keyword_map.yaml 에 하고 싶은 말을 한 줄 추가하고,
  이 노드를 Ctrl+C 로 끈 뒤 다시 켜세요. **다시 빌드할 필요 없습니다.**

■ 마이크 없이 시험하기
  다른 터미널에서:
      ros2 topic pub --once /stt_result std_msgs/msg/String "data: '기어 2번 집어'"
      ros2 topic echo /robot_command
"""

import os

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from std_msgs.msg import String


# ══════════════════════════════════════════════════════════
#  ▼▼▼ 여기를 바꿔가며 연습하세요 ▼▼▼
# ══════════════════════════════════════════════════════════

# 번호를 말하지 않았을 때 몇 번으로 볼까?
#   0 이면 "번호를 말해주세요" 라고 알려줍니다
DEFAULT_NUMBER = 0

# 못 알아들은 말도 화면에 보여줄까?
SHOW_UNKNOWN = True

# ══════════════════════════════════════════════════════════


def load_keyword_map(logger):
    """keyword_map.yaml 을 읽어온다."""
    path = os.path.join(
        get_package_share_directory("voice_robot_control"),
        "config", "keyword_map.yaml")

    if not os.path.isfile(path):
        logger.error(f"키워드 파일이 없습니다: {path}")
        return None

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f" ({mark.line + 1}째 줄 근처)" if mark else ""
        logger.error(
            f"keyword_map.yaml 을 읽지 못했습니다{where}.\n"
            "  · 낱말 앞의 '- ' 를 빠뜨리지 않았는지\n"
            "  · 띄어쓰기(들여쓰기) 칸수가 위아래와 같은지\n"
            "  확인해 보세요.\n"
            f"  [자세한 내용] {e}")
        return None
    except Exception as e:
        logger.error(f"keyword_map.yaml 을 읽지 못했습니다: {e}")
        return None

    logger.info(f"키워드 파일을 읽었습니다:\n  {path}")
    return data


def flatten(section: dict) -> list:
    """
    {이름: [낱말들]} 을  [(낱말, 이름), ...] 로 펴고 **긴 낱말부터** 정렬한다.

    긴 것부터 보는 이유:
      "왼쪽" 보다 "왼" 을 먼저 보면 "왼쪽으로" 가 그냥 "왼" 으로 잡힌다.
      항상 긴 낱말을 먼저 확인해야 한다.
    """
    pairs = []
    for name, words in (section or {}).items():
        for word in (words or []):
            pairs.append((str(word).replace(" ", "").lower(), name))
    return sorted(pairs, key=lambda p: len(p[0]), reverse=True)


def find(pairs, text):
    """text 안에 있는 낱말을 찾는다. (찾은낱말, 이름) 또는 (None, None)."""
    for word, name in pairs:
        if word and word in text:
            return word, name
    return None, None


def check_words(data, logger):
    """
    학생이 추가한 낱말에 문제가 없는지 봐 준다.

    가장 흔한 두 가지 실수를 잡는다.
      · 너무 짧은 낱말   "다" 한 글자를 넣으면 "가져다놔" 같은 말에도 걸린다
      · 같은 낱말 중복   두 곳에 같은 낱말을 넣으면 하나만 쓰인다
    """
    def collect(groups, label):
        out = []
        for name, words in (groups or {}).items():
            for word in (words or []):
                out.append((str(word).replace(" ", "").lower(), f"{label}/{name}"))
        return out

    # '무엇을 할지' 를 찾는 낱말들
    what = (collect(data.get("commands"), "명령")
            + collect(data.get("directions"), "방향"))

    # '몇 번인지' 를 찾는 낱말들
    which = collect(data.get("numbers"), "번호")
    which += [(str(w).replace(" ", "").lower(), "전체")
              for w in (data.get("all_words") or [])]

    problems = []

    # ── ① 같은 낱말이 두 곳에 있나 ────────────────────
    seen = {}
    for word, place in what + which:
        seen.setdefault(word, []).append(place)
    for word, places in sorted(seen.items()):
        if len(places) > 1:
            problems.append(
                f'"{word}" 가 여러 곳에 있습니다: {", ".join(places)} '
                f'→ 맨 앞 것만 쓰입니다')

    # ── ② 번호 낱말이 명령 낱말 안에 숨어 있나 ────────
    # 이게 진짜 위험한 경우다.
    # 예) 전체를 뜻하는 "다" 가 "가져다놔" 안에 들어 있으면,
    #     "기어 1번 가져다놔" 라고 해도 4개를 전부 해버린다.
    # 두 낱말은 서로 다른 단계에서 찾기 때문에, 긴 낱말 우선 규칙으로도 못 막는다.
    for small, small_place in which:
        for big, big_place in what:
            if small != big and small in big:
                problems.append(
                    f'"{small}" ({small_place}) 가 "{big}" ({big_place}) 안에 '
                    f'들어 있습니다 → "{big}" 라고만 말해도 '
                    f'"{small}" 를 말한 것으로 봅니다. 낱말을 더 길게 바꾸세요')

    if problems:
        logger.warn(
            "키워드에 손봐야 할 곳이 있습니다:\n  · " + "\n  · ".join(problems))
    return problems


class Parser:
    """글자를 명령으로 바꾸는 사람."""

    def __init__(self, data):
        self.commands = flatten(data.get("commands"))
        self.directions = flatten(data.get("directions"))
        self.numbers = flatten(
            {str(k): v for k, v in (data.get("numbers") or {}).items()})
        self.all_words = sorted(
            [str(w).replace(" ", "").lower() for w in (data.get("all_words") or [])],
            key=len, reverse=True)

    def parse(self, raw: str):
        """
        글자 → (명령, 설명줄들)

        명령을 못 만들면 (None, 설명줄들) 을 돌려준다.
        """
        text = raw.replace(" ", "").lower()
        steps = []

        # ── 1) 먼저 '무엇을 할지' 를 찾는다 ────────────────
        # 방향보다 명령을 먼저 본다. 그래야 "위로 조립해" 가
        # '위'(방향)가 아니라 '조립'(명령)으로 잡힌다.
        word, command = find(self.commands, text)
        if command:
            steps.append(f'명령어 찾기   "{word}" → {command}')

        # ── 2) 명령이 없으면 '방향' 을 본다 ───────────────
        if not command:
            word, direction = find(self.directions, text)
            if direction:
                steps.append(f'방향 찾기     "{word}" → {direction}')
                return f"jog {direction}", steps
            steps.append("아는 낱말이 하나도 없습니다")
            return None, steps

        # ── 3) 번호가 필요한 명령이면 번호를 찾는다 ───────
        if command in ("pick", "place", "pickplace"):
            # 번호를 '전체' 보다 먼저 본다.
            # "기어 1번 가져다놔" 처럼 번호를 콕 집어 말했으면
            # 그게 '전체' 보다 우선이어야 한다.
            word, number = find(self.numbers, text)
            if number:
                steps.append(f'번호 찾기     "{word}" → {number}번')
                return f"{command} {number}", steps

            for word in self.all_words:
                if word in text:
                    steps.append(f'번호 찾기     "{word}" → 전체')
                    return f"{command} all", steps

            if DEFAULT_NUMBER > 0:
                steps.append(f"번호 찾기     (없음) → {DEFAULT_NUMBER}번 으로 봄")
                return f"{command} {DEFAULT_NUMBER}", steps

            steps.append("번호 찾기     ✗ 몇 번인지 말해주세요 (예: 기어 2번 집어)")
            return None, steps

        # ── 4) 번호가 필요 없는 명령 ──────────────────────
        return command, steps


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("nlp_node")
    logger = node.get_logger()

    logger.info("=== ⑦ 말을 명령으로 바꾸기 시작 ===")

    data = load_keyword_map(logger)
    if data is None:
        rclpy.shutdown()
        return

    check_words(data, logger)

    parser = Parser(data)
    logger.info(
        f"알고 있는 낱말: 명령 {len(parser.commands)}개, "
        f"방향 {len(parser.directions)}개, 번호 {len(parser.numbers)}개")

    pub = node.create_publisher(String, "/robot_command", 10)

    def on_text(msg: String):
        raw = msg.data.strip()
        if not raw:
            return

        command, steps = parser.parse(raw)

        lines = [f'[들은 말] "{raw}"']
        for i, step in enumerate(steps):
            mark = "└" if (i == len(steps) - 1 and command is None) else "├"
            lines.append(f"   {mark} {step}")

        if command is None:
            if SHOW_UNKNOWN:
                logger.warn("\n".join(lines))
            return

        lines.append(f"   └ 만들어진 명령  >>> {command}")
        logger.info("\n".join(lines))

        out = String()
        out.data = command
        pub.publish(out)

    node.create_subscription(String, "/stt_result", on_text, 10)

    logger.info(
        "\n"
        "════════════════════════════════════════\n"
        "  /stt_result 를 기다립니다\n"
        "  끝내려면 Ctrl+C\n"
        "════════════════════════════════════════")

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("=== ⑦ 말을 명령으로 바꾸기 끝 ===")
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def try_once(sentences):
    """
    로봇도 ROS도 없이, 문장 하나가 어떤 명령이 되는지만 확인한다.

        python3 nlp_node.py "기어 2번 집어"
    """
    class PrintLogger:
        def info(self, m): print(m)
        def warn(self, m): print("[경고] " + m)
        def error(self, m): print("[오류] " + m)

    logger = PrintLogger()
    data = load_keyword_map(logger)
    if data is None:
        return 1

    check_words(data, logger)
    parser = Parser(data)

    for raw in sentences:
        command, steps = parser.parse(raw)
        print(f'\n[들은 말] "{raw}"')
        for step in steps:
            print(f"   · {step}")
        print(f"   → {command if command else '(명령을 만들지 못했습니다)'}")
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        sys.exit(try_once(sys.argv[1:]))
    main()

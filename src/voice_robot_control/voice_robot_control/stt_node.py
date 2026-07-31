#!/usr/bin/env python3
"""
stt_node.py — ⑥ 음성 인식 노드 (로봇에게 '귀' 달아주기)  [Module-6]

마이크로 들은 말을 글자로 바꿔 준다.
바꾼 글자는 화면에 찍고, 동시에 /stt_result 로 내보낸다.
(나중에 ⑦ 자연어 처리 노드가 이걸 받아서 로봇 명령으로 바꾼다)

    ros2 launch voice_robot_control stt.launch.py

로봇 팔이 필요 없으므로 로봇을 안 켜도 실행됩니다.
인터넷은 필요합니다 (구글 음성 인식 서버를 씁니다).

■ 실습
  · ENERGY_THRESHOLD 를 바꿔가며 감도를 조절해 보세요.
      너무 낮으면 → 주변 소음도 말로 알아듣습니다
      너무 높으면 → 크게 말해도 못 알아듣습니다
  · PAUSE_THRESHOLD 를 바꿔 "말이 끝났다" 고 판단하는 시간을 조절해 보세요.
  · LANGUAGE 를 "en-US" 로 바꿔 영어로도 해 보세요.

■ 마이크 없이 시험하기
  다른 터미널에서 아래처럼 치면, 말한 것과 똑같은 효과가 납니다.

      ros2 topic pub --once /stt_result std_msgs/msg/String "data: '기어 1번 집어'"

  잘 들리는지 확인만 하려면:

      ros2 topic echo /stt_result
"""

import rclpy
from rclpy.logging import get_logger
from std_msgs.msg import String

try:
    import speech_recognition as sr
except ImportError:
    raise SystemExit(
        "speech_recognition 이 없습니다.\n"
        "  설치: pip install SpeechRecognition pyaudio"
    )


# ══════════════════════════════════════════════════════════
#  ▼▼▼ 여기를 바꿔가며 연습하세요 ▼▼▼
# ══════════════════════════════════════════════════════════

# 무슨 말로 알아들을까?   한국어 "ko-KR" / 영어 "en-US"
LANGUAGE = "ko-KR"

# 얼마나 큰 소리부터 '말' 로 볼까? (감도)
#   0  = 시작할 때 주변 소음을 2초 들어보고 알아서 정함  ← 권장
#   숫자를 직접 적으면 그 값으로 고정됩니다 (예: 300, 1000, 4000)
ENERGY_THRESHOLD = 0

# 주변 소음이 변하면 감도를 계속 따라가게 할까?
AUTO_ADJUST = True

# 이만큼 조용해지면 '말이 끝났다' 고 본다 [초]
PAUSE_THRESHOLD = 0.8

# 한 번에 최대 몇 초까지 들을까? [초]
PHRASE_TIME_LIMIT = 5.0

# 쓸 마이크 번호.  -1 이면 시스템 기본 마이크
#   실행하면 쓸 수 있는 마이크 목록이 화면에 나옵니다. 거기서 골라 번호를 적으세요.
MIC_INDEX = -1

# ══════════════════════════════════════════════════════════


def show_microphones(logger):
    """쓸 수 있는 마이크 목록을 보여준다."""
    try:
        names = sr.Microphone.list_microphone_names()
    except Exception as e:
        logger.warning(f"마이크 목록을 읽지 못했습니다: {e}")
        return

    lines = [f"쓸 수 있는 마이크 {len(names)}개:"]
    for i, name in enumerate(names):
        mark = "  ◀ 지금 이걸 씁니다" if i == MIC_INDEX else ""
        lines.append(f"   [{i}] {name}{mark}")
    if MIC_INDEX < 0:
        lines.append("   → MIC_INDEX = -1 이라 시스템 기본 마이크를 씁니다.")
    logger.info("\n".join(lines))


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("stt_node")
    logger = node.get_logger()
    pub = node.create_publisher(String, "/stt_result", 10)

    logger.info("=== ⑥ 음성 인식 시작 ===")
    show_microphones(logger)

    # ── 인식기 설정 ─────────────────────────────────────
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = PAUSE_THRESHOLD
    recognizer.dynamic_energy_threshold = AUTO_ADJUST

    device = MIC_INDEX if MIC_INDEX >= 0 else None

    try:
        mic = sr.Microphone(device_index=device)
    except Exception as e:
        logger.error(
            f"마이크를 열지 못했습니다: {e}\n"
            "  · 마이크가 꽂혀 있는지 확인하세요\n"
            "  · 위 목록에서 번호를 골라 MIC_INDEX 에 적어 보세요"
        )
        rclpy.shutdown()
        return

    with mic as source:
        # ── 감도 정하기 ─────────────────────────────────
        if ENERGY_THRESHOLD > 0:
            recognizer.energy_threshold = ENERGY_THRESHOLD
            logger.info(f"감도를 {ENERGY_THRESHOLD} 로 고정했습니다.")
        else:
            logger.info("주변 소음을 2초 동안 들어봅니다. 조용히 해 주세요 ...")
            recognizer.adjust_for_ambient_noise(source, duration=2.0)
            logger.info(
                f"감도를 {recognizer.energy_threshold:.0f} 로 정했습니다.\n"
                "  (이 값보다 큰 소리를 '말' 로 봅니다)"
            )

        logger.info(
            "\n"
            "════════════════════════════════════════\n"
            "  이제 마이크에 말해 보세요\n"
            "  끝내려면 Ctrl+C\n"
            "════════════════════════════════════════"
        )

        # ── 듣고 → 글자로 바꾸고 → 내보내기 ─────────────
        while rclpy.ok():
            try:
                logger.info("듣는 중 ...")
                audio = recognizer.listen(
                    source, timeout=None, phrase_time_limit=PHRASE_TIME_LIMIT)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"마이크에서 소리를 못 받았습니다: {e}")
                continue

            try:
                text = recognizer.recognize_google(audio, language=LANGUAGE)
            except sr.UnknownValueError:
                logger.info("  (무슨 말인지 못 알아들었습니다)")
                continue
            except sr.RequestError as e:
                logger.error(
                    f"구글 음성 인식 서버에 연결하지 못했습니다: {e}\n"
                    "  · 인터넷이 연결돼 있는지 확인하세요"
                )
                continue
            except KeyboardInterrupt:
                break

            logger.info(f'  >>> 들은 말: "{text}"')

            msg = String()
            msg.data = text
            pub.publish(msg)

    logger.info("=== ⑥ 음성 인식 끝 ===")
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()

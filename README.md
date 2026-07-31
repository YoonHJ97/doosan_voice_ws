# doosan_voice_ws

두산 협동로봇(M0609)을 **말로 움직이는** ROS 2 워크스페이스입니다.
특강 *"AI가 로봇에게 귀와 입을 달아주다 — STT·TTS"* 실습용으로,
ROS 2를 처음 접하는 학생이 **YAML 파일만 고쳐서** 로봇을 다룰 수 있게 만들었습니다.

```
마이크 → 음성 인식 → 말을 명령으로 → 로봇 동작
        (STT)        (NLP)         (MoveIt2 + RG2)
```

## 들어 있는 노드

| | 노드 | 하는 일 | 로봇 필요 |
|---|---|---|:---:|
| ① | `move_node` | 좌표 한 곳으로 이동 | ○ |
| ② | `waypoint_node` | 여러 지점 순서대로 | ○ |
| ③ | `gripper_node` | 그리퍼만 열고 닫기 | — |
| ④ | `pick_place_node` | 물건 하나를 집어서 옮기기 | ○ |
| ⑤ | `gear_assembly_node` | 기어 여러 개 조립 | ○ |
| ⑥ | `stt_node` | 말을 알아듣고 글자로 | — |
| ⑦ | `nlp_node` | 글자를 로봇 명령으로 | — |
| ⑧ | `voice_robot_node` | 명령을 받아 실제로 움직이기 | ○ |
| | `position_viewer` | 손끝 위치 보기 | — |

난이도 순서대로 배우도록 되어 있습니다. ①~⑤는 코드를 읽고 고치는 실습,
⑥~⑧은 함께 켜서 말로 로봇을 움직이는 통합 실습입니다.

## 내려받기

처음 받을 때 — **홈 폴더에서** 받아야 `~/doosan_voice_ws` 가 됩니다.

```bash
cd ~
git clone https://github.com/YoonHJ97/doosan_voice_ws.git
cd doosan_voice_ws
```

이미 받아 놨다면, 최신 내용으로 갱신할 때

```bash
cd ~/doosan_voice_ws
git pull
```

> 내가 고친 파일이 있어서 `git pull` 이 거부되면, 내 것을 잠깐 치워두고 받은 뒤 되돌립니다.
>
> ```bash
> git stash          # 내가 고친 것 잠시 보관
> git pull
> git stash pop      # 다시 꺼내오기
> ```
>
> 내가 고친 것을 버리고 원본으로 되돌리려면
>
> ```bash
> git checkout -- src/voice_robot_control/config/keyword_map.yaml
> ```

## 한 번만 설정 — 터미널마다 source 안 하기

터미널을 열 때마다 `source` 를 치는 게 번거로우면 `~/.bashrc` 맨 아래에
아래 두 줄을 넣어 두세요. 그다음부터는 새 터미널에서 바로 쓸 수 있습니다.

```bash
# 두산 음성 로봇 워크스페이스
[ -f ~/doosan_voice_ws/install/setup.bash ] && source ~/doosan_voice_ws/install/setup.bash
```

한 줄로 넣는 명령

```bash
echo '[ -f ~/doosan_voice_ws/install/setup.bash ] && source ~/doosan_voice_ws/install/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

> `[ -f ... ] &&` 를 앞에 붙인 이유는 **아직 빌드하기 전**이라도 오류가 안 나게 하기 위해서입니다.
> 이게 없으면 `colcon build` 전에는 새 터미널마다 빨간 오류가 뜹니다.

이 한 줄이 ROS 2 → `moveit_py` → 두산 패키지 → 이 워크스페이스를 **전부** 끌어옵니다.
따로 `ros2_ws` 나 `ws_moveit` 을 source 하지 마세요.

> **주의 — `ws_moveit` 은 절대 넣지 마세요.**
> `~/ws_moveit` 은 옛 라이브러리로 빌드돼 있어서, source 하면 정상 MoveIt 을 가려
> `move_group` 이 죽고 RViz 플러그인이 안 뜹니다.
> `~/ros2_ws/install/setup.bash` 도 안에서 `ws_moveit` 을 끌어오므로 쓰지 마세요.
> (`local_setup.bash` 는 괜찮습니다)
>
> 지금 터미널이 오염됐는지 확인하는 법
>
> ```bash
> echo $AMENT_PREFIX_PATH | tr ':' '\n' | grep ws_moveit   # 아무것도 안 나와야 정상
> ```
>
> 한 줄이라도 나오면 그 터미널은 못 씁니다. `source` 는 경로를 덧붙일 뿐
> 지우지 않으므로 **새 터미널**을 열어야 합니다.

## 빠르게 해 보기

```bash
cd ~/doosan_voice_ws
colcon build --symlink-install
source install/setup.bash

# 터미널 1 — 로봇 (시뮬레이터)
ros2 launch dsr_bringup2 dsr_bringup2_moveit.launch.py mode:=virtual model:=m0609

# 터미널 2 — 말로 움직이기
ros2 launch voice_robot_control voice.launch.py
```

마이크가 없으면 타이핑으로도 됩니다.

```bash
ros2 launch voice_robot_control voice.launch.py use_stt:=false
ros2 topic pub --once /stt_result std_msgs/msg/String "data: '기어 2번 집어'"
```

## 학생이 고치는 파일

파이썬을 건드리지 않고 두 파일만 고치면 됩니다. **다시 빌드하지 않습니다.**

| 파일 | 정하는 것 |
|---|---|
| `config/keyword_map.yaml` | 어떤 **말**을 어떤 명령으로 볼지 |
| `config/my_actions.yaml` | 우리 팀이 만드는 새 **동작** |

```yaml
# my_actions.yaml — 동작 만들기
actions:
  인사:
    - 홈
    - 이동: {x: 0.40, y:  0.15, z: 0.50}
    - 이동: {x: 0.40, y: -0.15, z: 0.50}
    - 홈

# keyword_map.yaml — 그 동작을 부를 말 붙이기
commands:
  인사:
    - 인사해
    - 안녕
```

바꾼 낱말이 잘 먹히는지는 로봇·ROS 없이 바로 확인할 수 있습니다.

```bash
python3 src/voice_robot_control/voice_robot_control/nlp_node.py "안녕"
```

## 자세한 사용법

**→ [`src/voice_robot_control/README.md`](src/voice_robot_control/README.md)**

설치·실행 방법, 노드별 실습 내용, 안전 설정, 문제 해결이 모두 정리돼 있습니다.

## 필요한 환경

- Ubuntu 22.04 / ROS 2 Humble
- MoveIt 2 (`sudo apt install ros-humble-moveit`) + `moveit_py`
- [doosan-robot2](https://github.com/doosan-robotics/doosan-robot2) (M0609)
- OnRobot RG2 그리퍼 (없어도 시늉 모드로 실습 가능)
- `pip install SpeechRecognition pyaudio gtts pygame "pymodbus==2.5.3"`

## 라이선스

Apache-2.0

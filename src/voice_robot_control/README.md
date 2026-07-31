# voice_robot_control — 파이썬으로 로봇 움직이기

특강 **Module-5 / 6 / 7** 용 패키지입니다. `dsr_practice` 의 코드를 바탕으로,
수업에서 바로 고쳐 쓸 수 있게 다시 정리했습니다.

## 노드 8개 + 1개

| 노드 | 하는 일 | 로봇 팔 | 그리퍼 |
|------|---------|:---:|:---:|
| ① `move_node` | 홈으로 갔다가 좌표 한 곳으로 이동 | ○ | — |
| ② `waypoint_node` | 여러 지점을 순서대로 지나가기 | ○ | — |
| ③ `gripper_node` | 집게만 열고 닫기 | — | ○ |
| ④ `pick_place_node` | 물건 하나를 집어서 옮기기 | ○ | ○ |
| ⑤ `gear_assembly_node` | 기어 여러 개를 순서대로 조립 | ○ | ○ |
| ⑥ `stt_node` | 말을 알아듣고 글자로 바꾸기 | — | — |
| ⑦ `nlp_node` | 글자를 로봇 명령으로 바꾸기 | — | — |
| ⑧ `voice_robot_node` | **명령을 받아 실제로 로봇을 움직이기** | ○ | ○ |
| `position_viewer` | 손끝이 지금 어디 있는지 보여주기 | — | — |

**①→②→③→④→⑤ 순서로 배웁니다.**
①을 여러 번 이어 붙이면 ②, ①과 ③을 합치면 ④, ④를 여러 번 반복하면 ⑤ 입니다.
⑥⑦⑧ 을 함께 켜면 **말 한 마디로 로봇이 움직입니다.**

```
마이크 → ⑥ stt_node → /stt_result → ⑦ nlp_node → /robot_command → ⑧ voice_robot_node → 로봇
```

---

## 1. 빌드 (처음 한 번만)

```bash
cd ~/doosan_voice_ws
colcon build --symlink-install
```

> `--symlink-install` 덕분에 **`.py` 파일을 고친 뒤 다시 빌드하지 않아도 됩니다.**
> 고치고 바로 다시 실행하면 반영됩니다.

## 2. 실행

**터미널마다 이 한 줄을 먼저 칩니다.**

```bash
source ~/doosan_voice_ws/install/setup.bash
```

> **`ws_moveit` 은 source 하지 마세요.** 옛날 라이브러리로 빌드돼 있어서
> 정상 MoveIt 을 가려 버립니다. `move_group` 이 죽거나 RViz 플러그인이
> 안 뜨면 이걸 의심하세요. 확인 방법:
> ```bash
> echo $AMENT_PREFIX_PATH | tr ':' '\n' | grep ws_moveit   # 아무것도 안 나와야 정상
> ```

**터미널 1 — 로봇 켜기**  (③ 그리퍼 노드만 쓸 때는 생략 가능)

```bash
# 시뮬레이터
ros2 launch dsr_bringup2 dsr_bringup2_moveit.launch.py mode:=virtual model:=m0609

# 실제 로봇
ros2 launch dsr_bringup2 dsr_bringup2_moveit.launch.py \
  mode:=real model:=m0609 host:=192.168.1.100
```

**터미널 2 — 하고 싶은 것 하나 고르기**

```bash
ros2 launch voice_robot_control move.launch.py       # ① 단순 이동
ros2 launch voice_robot_control waypoint.launch.py   # ② 여러 지점
ros2 launch voice_robot_control gripper.launch.py    # ③ 그리퍼만
ros2 launch voice_robot_control pick_place.launch.py # ④ 집어서 옮기기
ros2 launch voice_robot_control gear.launch.py       # ⑤ 기어 조립
ros2 launch voice_robot_control stt.launch.py        # ⑥ 음성 인식
ros2 launch voice_robot_control nlp.launch.py        # ⑦ 말 → 명령
ros2 launch voice_robot_control voice_robot.launch.py # ⑧ 명령 → 로봇 동작
ros2 launch voice_robot_control voice.launch.py      # ⑥⑦⑧ 한 번에
ros2 launch voice_robot_control viewer.launch.py     # 손끝 위치 보기
```

①~⑤ 는 한 번에 **하나만** 켜고, 할 일을 다 하면 스스로 끝납니다.
⑥⑦⑧ 은 계속 켜 두는 노드라 **셋을 각각 다른 터미널에서 동시에** 켭니다. Ctrl+C 로 끕니다.

### 말로 로봇 움직이기 (터미널 2개)

```bash
# 1  로봇 켜기 (위와 동일)
# 2  ros2 launch voice_robot_control voice.launch.py    ← 6,7,8 을 한 번에
```

마이크 없이 타이핑으로 시험할 때는 6 을 빼고 켭니다.

```bash
ros2 launch voice_robot_control voice.launch.py use_stt:=false
# 다른 터미널에서
ros2 topic pub --once /stt_result std_msgs/msg/String "data: '기어 2번 집어'"
```

셋을 **따로** 켜고 싶으면 (어디가 문제인지 찾을 때는 이쪽이 낫습니다)

```bash
ros2 launch voice_robot_control voice_robot.launch.py   # 8
ros2 launch voice_robot_control nlp.launch.py           # 7
ros2 launch voice_robot_control stt.launch.py           # 6
```

말할 것: "홈으로" / "기어 2번 집어" / "전체 조립해" / "앞으로" / "정지"

---

## 3. 실습 — 코드 고쳐 보기

각 파일 맨 위에 `▼▼▼ 여기를 바꿔가며 연습하세요 ▼▼▼` 구역이 있습니다.
**그 아래 숫자만 고치면 됩니다.** 나머지는 안 건드려도 됩니다.

### ① `move_node.py`

```python
TARGET = {"x": 0.500, "y": 0.000, "z": 0.500}   # 어디로 갈까? [m]
SPEED = 0.15                                     # 얼마나 빠르게? (작을수록 느림)
```

### ② `waypoint_node.py`

```python
WAYPOINTS = [                       # 지나갈 지점들. 줄을 더 넣으면 늘어납니다
    {"x": 0.493, "y":  0.010, "z": 0.417},
    {"x": 0.493, "y": -0.218, "z": 0.417},
]
REPEAT = 1                          # 몇 바퀴?
RETURN_HOME = True                  # 끝나고 홈으로?
```

### ③ `gripper_node.py`

```python
USE_GRIPPER = True    # True 면 진짜 움직임. False 면 시늉만
OPEN_WIDTH = 500      # 열었을 때 50mm   ※ 단위가 1/10 mm 입니다
CLOSE_WIDTH = 150     # 닫았을 때 15mm
FORCE = 300           # 쥐는 힘 30N     ※ 단위가 1/10 N 입니다
MAX_RETRY = 3         # 못 잡으면 몇 번까지 다시?
```

> **단위 주의** — 그리퍼만 `1/10 mm`, `1/10 N` 을 씁니다.
> `500` 은 50mm, `300` 은 30N 입니다. RG2 하드웨어가 그렇게 받습니다.

> ③④⑤ 세 노드 모두 **닫힘 15mm / 힘 30N** 으로 같습니다.
> ③에서 잡히는 값이 ④⑤에서도 그대로 통합니다.

### ④ `pick_place_node.py`

```python
PICK  = {"x": 0.427, "y":  0.148, "z": 0.280}   # 어디서 집을까?
PLACE = {"x": 0.426, "y": -0.153, "z": 0.280}   # 어디에 놓을까?
APPROACH_OFFSET = 0.05                           # 위에서 접근하는 높이 [m]
USE_GRIPPER = True
```

### ⑤ `gear_assembly_node.py`

```python
GEAR_TASKS = [
    {"pick":  {"x": 0.393, "y":  0.094, "z": 0.280},
     "place": {"x": 0.393, "y": -0.206, "z": 0.280}},
    ...
]
APPROACH_OFFSET = 0.05     # 위에서 접근하는 높이 [m]
USE_WIGGLE = True          # 마지막 기어를 좌우로 흔들어 끼울까?
USE_GRIPPER = True         # 실제 그리퍼를 쓸까?
```

### ⑥ `stt_node.py`

```python
LANGUAGE = "ko-KR"        # 한국어. 영어로 하려면 "en-US"
ENERGY_THRESHOLD = 0      # 0 = 시작할 때 주변 소음에 맞춰 자동으로 정함
PAUSE_THRESHOLD = 0.8     # 이만큼 조용해지면 '말이 끝났다'
PHRASE_TIME_LIMIT = 5.0   # 한 번에 최대 몇 초까지 들을까
MIC_INDEX = -1            # -1 = 기본 마이크. 실행하면 목록이 나옵니다
```

> **감도(`ENERGY_THRESHOLD`) 가 이 실습의 핵심입니다.**
> 이 컴퓨터에서 자동 측정하면 **4000~5500** 쯤 나옵니다. 기본값 300 을 그대로 쓰면
> 주변 소음까지 전부 말로 알아들어 버립니다. 조용한 곳이면 낮게, 시끄러우면 높게.

마이크가 없거나 안 될 때는 말한 것처럼 흉내낼 수 있습니다.

```bash
ros2 topic pub --once /stt_result std_msgs/msg/String "data: '기어 1번 집어'"
ros2 topic echo /stt_result       # 잘 들리는지 확인만
```

### ⑦ `nlp_node.py` 와 `config/keyword_map.yaml`

무슨 말을 알아들을지는 **`config/keyword_map.yaml`** 에 적혀 있습니다.
낱말을 추가하고 노드를 껐다 켜면 끝입니다. **다시 빌드하지 않습니다.**

```yaml
commands:
  pickplace:
    - 조립
    - 옮겨
    - 우리팀만의말     # ← 이렇게 한 줄 추가
```

바뀌는 과정이 화면에 그대로 나옵니다.

```
[들은 말] "기어 2번 집어줘"
   ├ 명령어 찾기   "집어줘" → pick
   ├ 번호 찾기     "2번" → 2번
   └ 만들어진 명령  >>> pick 2
```

만들어지는 명령: `home` / `pick N` / `place N` / `pickplace N` /
`pickplace all` / `jog forward` / `open` / `close` / `stop`

> **명령이 방향보다 먼저입니다.** "위로 조립해" 처럼 둘 다 들어 있으면
> '위'(방향)가 아니라 '조립'(명령)으로 봅니다.
> 그리고 긴 낱말을 먼저 확인하므로 "왼쪽" 이 "왼" 에 가려지지 않습니다.

#### 우리 팀 명령어 추가하기 — 4단계

**1. 파일 열기**

```bash
gedit ~/doosan_voice_ws/src/voice_robot_control/config/keyword_map.yaml
```

**2. 하고 싶은 말을 한 줄 추가** (원하는 항목 밑에 `- 낱말`)

```yaml
commands:
  pickplace:
    - 조립
    - 출발        # ← 우리 팀 말
```

**3. 미리 보기** — 로봇도 ROS도 마이크도 필요 없습니다

```bash
python3 ~/doosan_voice_ws/src/voice_robot_control/voice_robot_control/nlp_node.py "기어 2번 출발"
```

```
[들은 말] "기어 2번 출발"
   · 명령어 찾기   "출발" → pickplace
   · 번호 찾기     "2번" → 2번
   → pickplace 2
```

**4. 반영** — `nlp_node` 를 Ctrl+C 로 끄고 다시 켜기.
`install` 이 `src` 로 이어져 있어 **다시 빌드하지 않습니다.**

> **낱말 만들 때 주의**
> 짧은 낱말은 다른 말 속에 숨어듭니다. 예를 들어 '전체'를 뜻하는 낱말로
> `다` 를 넣으면 `가져다놔` 안에도 `다` 가 있어서, 1번만 시켜도 4개를 다 해버립니다.
> 노드를 켤 때 이런 경우를 자동으로 잡아 알려줍니다.
>
> ```
> · "다" (전체) 가 "가져다놔" (명령/pickplace) 안에 들어 있습니다
>   → "가져다놔" 라고만 말해도 "다" 를 말한 것으로 봅니다
> ```
>
> 들여쓰기를 틀렸을 때도 몇째 줄인지 알려줍니다.

#### 우리 팀 **동작**까지 새로 만들기 — 파일 2개

낱말만 바꾸는 게 아니라 **없던 동작을 새로 만들 수도** 있습니다.
파이썬은 건드리지 않습니다.

**1. `config/my_actions.yaml` 에 동작을 만든다**

```yaml
actions:
  인사:
    - 홈
    - 이동: {x: 0.40, y:  0.15, z: 0.50}
    - 이동: {x: 0.40, y: -0.15, z: 0.50}
    - 홈
```

쓸 수 있는 한 줄

| 줄 | 하는 일 |
|---|---|
| `- 홈` | 홈 자세로 |
| `- 이동: {x: 0.4, y: 0.0, z: 0.45}` | 그 좌표로 [m] |
| `- 관절: [0, 0, 90, 0, 90, 0]` | 관절 6개를 그 각도로 [도] |
| `- 집기: 2` / `- 놓기: 2` | 2번 기어 집기 / 놓기 |
| `- 열기` / `- 닫기` | 그리퍼 |
| `- 기다리기: 1.0` | 그만큼 쉬기 [초] |

**2. `config/keyword_map.yaml` 에 같은 이름으로 낱말을 붙인다**

```yaml
commands:
  인사:          # ← my_actions.yaml 의 이름과 똑같이
    - 인사해
    - 안녕
```

**3. `nlp_node` 와 `voice_robot_node` 를 껐다 켠다** (다시 빌드 안 함)

**4. "안녕" 이라고 말한다**

```
[들은 말] "안녕"  →  인사
우리 팀 동작 '인사' — 모두 4단계
  [1/4] 홈
  [2/4] 이동: {'x': 0.4, 'y': 0.15, 'z': 0.5}
  ...
>>> 인사 완료
```

예시로 `인사` / `집게운동` / `둘만옮기기` 세 개가 이미 만들어져 있습니다.
그대로 말해 보고, 숫자를 고쳐가며 우리 팀 동작을 만들면 됩니다.

> 좌표를 모르겠으면 위치 보기를 켜서 확인하세요.
> `ros2 launch voice_robot_control viewer.launch.py`

#### ⑥ 없이 ⑦ 만 써도 됩니다

⑦ 은 `/stt_result` 토픽을 구독할 뿐이라, 거기에 글자를 넣어주는 게
마이크든 손타이핑이든 상관없습니다.

```bash
ros2 topic pub --once /stt_result std_msgs/msg/String "data: '기어 2번 집어'"
```

| 켜는 것 | 할 수 있는 일 |
|---|---|
| ⑦ 만 | 글자가 어떤 명령이 되는지 확인 (로봇·마이크 불필요) |
| ⑦ + ⑧ | 타이핑으로 로봇을 실제로 움직임 (마이크 불필요) |
| ⑥ + ⑦ + ⑧ | 말로 로봇을 움직임 |
| ⑧ 만 | `/robot_command` 에 직접 넣어 움직임 |

#### 어디가 문제인지 찾기

```
말했는데 로봇이 안 움직인다
  → /stt_result 에 직접 넣어본다
      움직이면   → ⑥ 문제 (감도 / 마이크 번호 / 인터넷)
      안 움직이면 → ⑦ 또는 ⑧ 문제
```

```bash
ros2 topic echo /stt_result      # ⑥ 이 뭘 알아들었나
ros2 topic echo /robot_command   # ⑦ 이 뭘 만들었나
ros2 topic echo /robot_status    # ⑧ 이 뭘 했나
```

### ⑧ `voice_robot_node.py`

```python
GEAR_TASKS = [ ... ]       # 기어 좌표 (⑤ 와 같은 값)
APPROACH_OFFSET = 0.05     # 위에서 접근하는 높이 [m]
JOG_STEP = 0.05            # "앞으로" 한 번에 갈 거리 [m]
USE_GRIPPER = True
SPEED = 0.15
```

알아듣는 명령 (⑦ 이 만들어 보내는 것과 같습니다)

| 명령 | 뜻 |
|---|---|
| `home` | 홈 자세로 |
| `pick 2` / `place 2` | 2번 기어 집기 / 놓기 |
| `pickplace 2` | 2번 기어 집어서 옮기기 |
| `pickplace all` | 전체 기어 순서대로 |
| `jog forward` | 앞으로 조금 (backward/left/right/up/down) |
| `open` / `close` | 그리퍼 열기 / 닫기 |
| `stop` | 기다리는 명령 모두 취소 |

말 없이 직접 시켜볼 수도 있습니다.

```bash
ros2 topic pub --once /robot_command std_msgs/msg/String "data: 'pick 2'"
```

> **`stop` 은 기다리던 명령만 취소합니다.** 이미 시작한 동작은 끝까지 갑니다.
> 급할 때는 **비상정지 버튼**을 누르세요.

---

## 4. 좌표를 모를 때

터미널 3에서 위치 보기를 켜면 손끝이 지금 어디 있는지 계속 알려줍니다.

```bash
ros2 launch voice_robot_control viewer.launch.py
```

```
손끝 위치   x=+0.398  y=+0.096  z=+0.280  [m]
  손끝 방향   +180 / +0 / +180  [도]
  관절 각도   J1=+12  J2=+30  ...
```

이 숫자를 그대로 `TARGET` 이나 `GEAR_TASKS` 에 옮겨 적으면 됩니다.
이름을 붙여 파일로 남기고 싶으면:

```bash
ros2 topic pub --once /record_pose std_msgs/msg/String "data: '내자리'"
# → ~/내가_저장한_자세.yaml 에 쌓입니다
```

---

## 5. 안전장치

목표가 아래 범위를 벗어나면 **경계값으로 잘라내고 경고**를 띄웁니다.
`robot_common.py` 에 있습니다.

| 축 | 범위 [m] |
|----|----------|
| x | 0.0 이상 |
| y | -0.3 ~ 0.3 |
| z | 0.27 이상 |

처음 해 볼 때는 각 파일의 `SPEED` 를 `0.05` 정도로 낮추고 비상정지에 손을 올려 두세요.

---

## 6. 잘 안 될 때

| 화면에 뜨는 말 | 무엇을 확인할까 |
|---|---|
| `libgeometric_shapes.so.2.3.2: cannot open...` | `ws_moveit` 을 source 했습니다. 새 터미널을 여세요 |
| `Unable to configure planning scene monitor` | 터미널 1(로봇)이 안 떠 있습니다 |
| `가는 길을 찾지 못했습니다` | 로봇 팔이 닿지 않는 좌표입니다. 위치 보기로 확인 후 가까운 값부터 |
| `길은 찾았는데 로봇이 움직이지 않았습니다` | 계획은 됐지만 로봇이 거부했습니다. 비상정지 / 연결 확인 |
| `그리퍼에 연결하지 못했습니다` | `USE_GRIPPER = False` 로 두면 시늉만 하고 계속 진행합니다 |
| `마이크를 열지 못했습니다` | 화면의 마이크 목록에서 번호를 골라 `MIC_INDEX` 에 적으세요 |
| `구글 음성 인식 서버에 연결하지 못했습니다` | 인터넷 연결을 확인하세요 (⑥ 은 인터넷이 필요합니다) |
| 소음까지 계속 알아들음 | `ENERGY_THRESHOLD` 를 올리세요 (이 컴퓨터는 4000~5500 정도) |
| `아는 낱말이 하나도 없습니다` | `keyword_map.yaml` 에 그 말을 추가하고 ⑦ 을 다시 켜세요 |
| `몇 번인지 말해주세요` | "기어 2번 집어" 처럼 번호를 넣거나 "전체" 라고 하세요 |

---

## 7. 파일 구성

```
voice_robot_control/
├── move_node.py            ① 단순 이동
├── waypoint_node.py        ② 여러 지점
├── gripper_node.py         ③ 그리퍼
├── pick_place_node.py      ④ 집어서 옮기기
├── gear_assembly_node.py   ⑤ 기어 조립
├── stt_node.py             ⑥ 음성 인식
├── nlp_node.py             ⑦ 말 → 로봇 명령
├── voice_robot_node.py     ⑧ 명령 → 로봇 동작
├── position_viewer.py      손끝 위치 보기
│
├── robot_common.py         여러 노드가 함께 쓰는 부분
│                           (홈 자세, 안전 영역, 경로 계획+실행)
├── gripper_control.py      그리퍼 연결 (실물 없으면 시늉)
│
│  [학생이 고치는 파일]
│  config/keyword_map.yaml   어떤 말을 어떤 명령으로 볼지
│  config/my_actions.yaml    우리 팀이 만드는 새 동작
├── onrobot.py              OnRobot RG2 드라이버
├── pose_utils.py           각도 ↔ 쿼터니언 변환
└── launch_helper.py        launch 파일 공용 부분
```

로봇을 움직이는 방법 자체는 **`robot_common.py` 의 `plan_and_execute()` 한 곳**에
모여 있습니다. 모든 노드가 이 함수를 씁니다.

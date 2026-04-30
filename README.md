<h1 align="center">HEX FLOW REPLAY ARCHER Y6</h1>

<p align="center">
    <a href="https://github.com/hexfellow/hex_flow_replay_archer_y6/stargazers">
        <img src="https://img.shields.io/github/stars/hexfellow/hex_flow_replay_archer_y6?style=flat-square&logo=github" />
    </a>
    <a href="https://github.com/hexfellow/hex_flow_replay_archer_y6/forks">
        <img src="https://img.shields.io/github/forks/hexfellow/hex_flow_replay_archer_y6?style=flat-square&logo=github" />
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/hexfellow/hex_flow_replay_archer_y6/issues">
        <img src="https://img.shields.io/github/issues/hexfellow/hex_flow_replay_archer_y6?style=flat-square&logo=github" />
    </a>
</p>

---

# 📖 Overview

## What is `hex_flow_replay_archer_y6`

`hex_flow_replay_archer_y6` is a hex-flow node that replays recorded Archer Y6 arm and gripper trajectories from MCAP bag files. It orchestrates the robot through a four-phase lifecycle — **init**, **prep**, **run**, and **exit** — enabling deterministic replay of pre-recorded manipulation episodes on either real or simulated Archer Y6 hardware.

### Core lifecycle

1. **Init phase** — On startup, the node commands the arm and gripper to move to a configurable stable position, waiting until the robot arrives within a configurable error threshold.
2. **Work phase** — Once at the stable position, the node transitions into the main work loop:
   - **Load**: Parses the MCAP bag file specified by `MCAP_PATH`, extracting `arm_state` and `grip_state` time-series data with nanosecond timestamps.
   - **Prep**: Drives the robot to the bag's start position and, once stabilized, publishes a `record=True` signal to trigger an external data recording node (e.g., `hex_flow_node_data`).
   - **Run**: Replays the full trajectory by time-interpolating arm and gripper positions at each control cycle, publishing compensation-mode commands. When the bag ends, a `record=False` signal is published to stop recording.
3. **Exit phase** — On shutdown (triggered by pressing the `q` key or `Ctrl+C`), the node sends `record=False`, then commands the arm back to the stable position before exiting cleanly.

## What problem it solves

- **Deterministic replay**: Replay pre-recorded arm/gripper trajectories from MCAP bag files with time interpolation, enabling reproducible experiments and policy evaluations.
- **Data collection integration**: Publishes `record` (bool) topic to synchronize with a `hex_flow_node_data` node, automating the recording of replayed episodes.
- **Looping support**: Configure `LOOP_COUNT` to replay the same trajectory multiple times, useful for repeated trials or robustness testing.
- **Out-of-the-box control flow**: Provides a standard lifecycle (init → prep → run → exit) with graceful shutdown, eliminating boilerplate state machine logic.
- **Flexible deployment**: Supports both real robot hardware (via `hex_flow_node_robot`) and MuJoCo simulation (via `hex_flow_node_mujoco`) — just swap the robot source with zero code changes.

## Target users

- Data collection engineers replaying robot demonstration trajectories for imitation learning datasets.
- Researchers evaluating manipulation policies by replaying identical trajectories across multiple trials.
- Developers using the hex-flow framework looking for a reference implementation of a bag-based replay node.

## Nodes

| Node                          | Description                             | Publishes                           | Subscribes                          |
| ----------------------------- | --------------------------------------- | ----------------------------------- | ----------------------------------- |
| `hex-flow-replay-archer-y6`   | Archer Y6 replay node                   | `arm_ctrl`, `grip_ctrl`, `record`   | `arm_state`, `grip_state`, `keys`   |

> The optional `data_record` node (from `hex_flow_node_data`) can subscribe to `arm_state`, `grip_state`, and `record` topics to capture each replayed episode.

## Architecture diagram

```
┌─────────────────┐     arm_state / grip_state     ┌────────────────────────┐
│  Robot Source   │ ──────────────────────────────> │  hex-flow-replay-      │
│ (real or MuJoCo)│                                │  archer-y6             │
│                 │ <─────────────────────────────  │                        │
└─────────────────┘     arm_ctrl / grip_ctrl       └──────┬────────┬────────┘
                                                          │ record │ keys
                                                          │        │
                                           ┌──────────────▼──┐ ┌───▼─────────┐
                                           │  data_record    │ │teleop_kb    │
                                           │  (optional)     │ │             │
                                           └─────────────────┘ └─────────────┘
```

The replay node sits between a robot source (either `hex-flow-robot-archer-y6` for real hardware or `hex-flow-mujoco-archer-y6` for MuJoCo simulation) and a teleop keyboard node. It subscribes to robot state topics and keyboard events, and publishes control commands back to the robot source, along with a `record` signal to trigger external data recording.

# 📦 Installation

## Requirements

- **Python** >= 3.10
- **Core dependencies**:
  - `hex_flow_core` >= 0.0.0, < 0.1.0
  - `hex_flow_node_robot` >= 0.0.0, < 0.1.0
  - `hex_flow_node_teleop` >= 0.0.0, < 0.1.0
  - `hex_flow_node_mujoco` >= 0.0.0, < 0.1.0
  - `hex_flow_node_data` >= 0.0.0, < 0.1.0
  - `hex_util_data` >= 0.0.0, < 0.1.0
  - `hex_util_robot` >= 0.0.0, < 0.1.0

## Install `hex-flow-cli`

For Ubuntu or any Debian-based system, install Zenoh and hex-flow CLI:

```bash
sudo apt update
sudo apt install -y curl gpg

curl -L https://download.eclipse.org/zenoh/debian-repo/zenoh-public-key | sudo gpg --dearmor --yes --output /etc/apt/keyrings/zenoh-public-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/zenoh-public-key.gpg] https://download.eclipse.org/zenoh/debian-repo/ /" | sudo tee -a /etc/apt/sources.list > /dev/null
sudo apt update
sudo apt install zenoh curl

curl -fsSL https://raw.githubusercontent.com/hexfellow/hex-flow/main/install.sh | sh
```

For other systems, please install `zenohd` yourself, then run the [install script](https://raw.githubusercontent.com/hexfellow/hex-flow/main/install.sh).

## Install `hex-flow-replay-archer-y6` from source

We provide a [venv.sh](venv.sh) script to create a virtual environment with all dependencies installed. However, you need to install `uv` first. For `uv` installation, please refer to the `uv` official [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then you can use [venv.sh](venv.sh) to create a virtual environment with all dependencies installed:

```bash
git clone https://github.com/hexfellow/hex_flow_replay_archer_y6.git
cd hex_flow_replay_archer_y6
./venv.sh
```

# 📑 Python Config API

The package provides the `default_replay_archer_y6_node` helper function that returns a `NodeConfig` object for easy integration into your `LaunchConfig`.

## Real robot launch

```python
import os
from hex_flow_core import LaunchConfig
from hex_flow_node_robot import default_robot_archer_y6_node
from hex_flow_node_teleop import default_teleop_keyboard_node
from hex_flow_node_data import default_data_record_node
from hex_flow_replay_archer_y6 import default_replay_archer_y6_node

config = LaunchConfig(
    local_only=True,
    enable_tui=True,
    log_to_file=True,
    save_path="/tmp/real_replay.yml",
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

nodes = {
    "robot_archer_y6":
    default_robot_archer_y6_node(
        name="robot_archer_y6",
        host="172.18.27.26",
        port=9439,
        ctrl_rate=500,
        state_buffer_size=200,
        sens_ts=True,
        grip_type="gp80",
        pose_end_in_flange="0.187,0.0,0.0,1.0,0.0,0.0,0.0",
        required=True,
        hidden=True,
        remap_dict={
            "arm_state": "robot_archer_y6/arm_state",
            "grip_state": "robot_archer_y6/grip_state",
            "arm_ctrl": "robot_archer_y6/arm_ctrl",
            "grip_ctrl": "robot_archer_y6/grip_ctrl",
        },
    ),
    "teleop_keyboard":
    default_teleop_keyboard_node(
        name="teleop_keyboard",
        device_path="",
        rate_hz=100.0,
        required=True,
        hidden=True,
        remap_dict={"teleop_keyboard": "teleop_keyboard/teleop_keyboard"},
    ),
    "replay_archer_y6":
    default_replay_archer_y6_node(
        name="replay_archer_y6",
        rate_hz=500.0,
        arm_stable_pos="0.0,-1.5,3.0,0.07,0.0,0.0",
        grip_stable_pos="0.5",
        arrive_threshold=0.06,
        arm_err_threshold=0.04,
        grip_err_threshold=0.02,
        mcap_path=f"{SCRIPT_DIR}/replay_data/episode_000001.mcap",
        loop_count=1,
        required=True,
        hidden=False,
        remap_dict={
            "arm_state": "robot_archer_y6/arm_state",
            "grip_state": "robot_archer_y6/grip_state",
            "arm_ctrl": "robot_archer_y6/arm_ctrl",
            "grip_ctrl": "robot_archer_y6/grip_ctrl",
            "keys": "teleop_keyboard/teleop_keyboard",
            "record": "replay_archer_y6/record",
        },
    ),
    "data_record":
    default_data_record_node(
        name="data_record",
        record_path=f"{SCRIPT_DIR}/record_data",
        foxglove_host="127.0.0.1",
        foxglove_port=8765,
        start_cnt=0,
        required=False,
        remap_dict={
            "arm_state": "robot_archer_y6/arm_state",
            "grip_state": "robot_archer_y6/grip_state",
            "record": "replay_archer_y6/record",
        },
    ),
}

config.set_nodes(nodes)
print(config.export())
```

## MuJoCo simulation launch

```python
import os
from hex_flow_core import LaunchConfig
from hex_flow_node_mujoco import default_mujoco_archer_y6_node
from hex_flow_node_teleop import default_teleop_keyboard_node
from hex_flow_node_data import default_data_record_node
from hex_flow_replay_archer_y6 import default_replay_archer_y6_node

config = LaunchConfig(
    local_only=True,
    enable_tui=True,
    log_to_file=True,
    save_path="/tmp/sim_replay.yml",
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

nodes = {
    "mujoco_archer_y6":
    default_mujoco_archer_y6_node(
        name="mujoco_archer_y6",
        state_rate=500,
        cam_rate=30,
        headless=False,
        state_buffer_size=200,
        cam_buffer_size=8,
        sens_ts=False,
        camera_type="empty",
        rate_hz=500,
        required=True,
        hidden=True,
        remap_dict={
            "arm_state": "mujoco_archer_y6/arm_state",
            "grip_state": "mujoco_archer_y6/grip_state",
            "arm_ctrl": "mujoco_archer_y6/arm_ctrl",
            "grip_ctrl": "mujoco_archer_y6/grip_ctrl",
        },
    ),
    "teleop_keyboard":
    default_teleop_keyboard_node(
        name="teleop_keyboard",
        device_path="",
        rate_hz=100.0,
        required=True,
        hidden=True,
        remap_dict={"teleop_keyboard": "teleop_keyboard/teleop_keyboard"},
    ),
    "replay_archer_y6":
    default_replay_archer_y6_node(
        name="replay_archer_y6",
        rate_hz=500.0,
        arm_stable_pos="0.0,-1.5,3.0,0.07,0.0,0.0",
        grip_stable_pos="0.5",
        arrive_threshold=0.06,
        arm_err_threshold=0.04,
        grip_err_threshold=0.02,
        mcap_path=f"{SCRIPT_DIR}/replay_data/episode_000001.mcap",
        loop_count=1,
        required=True,
        hidden=False,
        remap_dict={
            "arm_state": "mujoco_archer_y6/arm_state",
            "grip_state": "mujoco_archer_y6/grip_state",
            "arm_ctrl": "mujoco_archer_y6/arm_ctrl",
            "grip_ctrl": "mujoco_archer_y6/grip_ctrl",
            "keys": "teleop_keyboard/teleop_keyboard",
            "record": "replay_archer_y6/record",
        },
    ),
    "data_record":
    default_data_record_node(
        name="data_record",
        record_path=f"{SCRIPT_DIR}/record_data",
        foxglove_host="127.0.0.1",
        foxglove_port=8765,
        start_cnt=0,
        required=False,
        remap_dict={
            "arm_state": "mujoco_archer_y6/arm_state",
            "grip_state": "mujoco_archer_y6/grip_state",
            "record": "replay_archer_y6/record",
        },
    ),
}

config.set_nodes(nodes)
print(config.export())
```

### `default_replay_archer_y6_node`

| Parameter           | Type    | Default                                          | Description                                         |
| ------------------- | ------- | ------------------------------------------------ | --------------------------------------------------- |
| `name`              | `str`   | `"replay_archer_y6"`                             | Node name and remap prefix                          |
| `rate_hz`           | `float` | `500.0`                                          | Control loop rate in Hz                             |
| `arm_stable_pos`    | `str`   | `"0.0,-1.5,3.0,0.07,0.0,0.0"`                   | Arm stable joint position (6-DOF comma-separated)   |
| `grip_stable_pos`   | `str`   | `"0.5"`                                          | Gripper stable position                             |
| `arm_kp`            | `str`   | `"200.0,200.0,250.0,150.0,100.0,100.0"`          | Arm stiffness gains (6-DOF comma-separated)         |
| `arm_kd`            | `str`   | `"5.0,5.0,5.0,5.0,2.0,2.0"`                     | Arm damping gains (6-DOF comma-separated)           |
| `grip_kp`           | `str`   | `"10.0"`                                          | Gripper stiffness gain                              |
| `grip_kd`           | `str`   | `"0.5"`                                           | Gripper damping gain                                |
| `arrive_threshold`  | `float` | `0.06`                                           | Joint position threshold (rad) to consider arrived  |
| `arm_err_threshold` | `float` | `0.02`                                           | Arm position error limit for safety (`lim_err`)     |
| `grip_err_threshold`| `float` | `0.02`                                           | Gripper position error limit for safety (`lim_err`) |
| `mcap_path`         | `str`   | `""`                                             | Path to the MCAP bag file to replay                 |
| `loop_count`        | `int`   | `1`                                              | Number of times to replay the trajectory            |
| `required`          | `bool`  | `True`                                           | Required for launch                                 |
| `hidden`            | `bool`  | `False`                                          | Hidden node                                         |
| `remap_dict`        | `dict`  | `None`                                           | Custom remap; defaults to `{robot_source}/*`        |
| `robot_source`      | `str`   | `"mujoco_archer_y6"`                             | Robot node to subscribe/publish to                  |
| `keys_source`       | `str`   | `"teleop_keyboard"`                              | Teleop keyboard node to subscribe to                |

# 💡 Examples

Ready-to-run config scripts are provided in the [`example/`](example/) directory. Each script prints a launch YAML to stdout, intended for use with `hexflow run`:

### Real robot

```bash
# 500 Hz replay loop with real Archer Y6 hardware
hexflow run example/real_replay.launch.py
```

### MuJoCo simulation

```bash
# 500 Hz replay loop with MuJoCo simulated Archer Y6
hexflow run example/sim_replay.launch.py
```

# YAML Examples

### Real robot (500 Hz)

```yaml
nodes:
  - name: robot_archer_y6
    build: pip install hex_flow_node_robot
    run: hex-flow-robot-archer-y6
    required: true
    hidden: true
    remap:
      arm_state: robot_archer_y6/arm_state
      grip_state: robot_archer_y6/grip_state
      arm_ctrl: robot_archer_y6/arm_ctrl
      grip_ctrl: robot_archer_y6/grip_ctrl
    env:
      HOST: "172.18.27.26"
      PORT: "9439"
      CTRL_RATE: "500"
      STATE_BUFFER_SIZE: "200"
      SEN_TS: "True"
      GRIP_TYPE: "gp80"
      POSE_END_IN_FLANGE: "0.187,0.0,0.0,1.0,0.0,0.0,0.0"

  - name: teleop_keyboard
    build: pip install hex_flow_node_teleop
    run: hex-flow-teleop-keyboard
    required: true
    hidden: true
    remap:
      teleop_keyboard: teleop_keyboard/teleop_keyboard
    env:
      DEVICE_PATH: ""

  - name: replay_archer_y6
    build: pip install hex_flow_replay_archer_y6
    run: hex-flow-replay-archer-y6
    required: true
    remap:
      arm_state: robot_archer_y6/arm_state
      grip_state: robot_archer_y6/grip_state
      arm_ctrl: robot_archer_y6/arm_ctrl
      grip_ctrl: robot_archer_y6/grip_ctrl
      keys: teleop_keyboard/teleop_keyboard
      record: replay_archer_y6/record
    env:
      RATE_HZ: "500"
      ARM_STABLE_POS: "0.0,-1.5,3.0,0.07,0.0,0.0"
      GRIP_STABLE_POS: "0.5"
      ARM_KP: "200.0,200.0,250.0,150.0,100.0,100.0"
      ARM_KD: "5.0,5.0,5.0,5.0,2.0,2.0"
      GRIP_KP: "10.0"
      GRIP_KD: "0.5"
      ARRIVE_THRESHOLD: "0.06"
      ARM_ERR_THRESHOLD: "0.04"
      GRIP_ERR_THRESHOLD: "0.02"
      MCAP_PATH: "/path/to/replay_data/episode_000001.mcap"
      LOOP_COUNT: "1"

  - name: data_record
    build: pip install hex_flow_node_data
    run: hex-flow-data-record
    required: false
    remap:
      arm_state: robot_archer_y6/arm_state
      grip_state: robot_archer_y6/grip_state
      record: replay_archer_y6/record
    env:
      RECORD_PATH: "/path/to/record_data"
      FOXGLOVE_HOST: "127.0.0.1"
      FOXGLOVE_PORT: "8765"
      START_CNT: "0"
```

### MuJoCo simulation (500 Hz)

```yaml
nodes:
  - name: mujoco_archer_y6
    build: pip install hex_flow_node_mujoco
    run: hex-flow-mujoco-archer-y6
    required: true
    hidden: true
    remap:
      arm_state: mujoco_archer_y6/arm_state
      grip_state: mujoco_archer_y6/grip_state
      arm_ctrl: mujoco_archer_y6/arm_ctrl
      grip_ctrl: mujoco_archer_y6/grip_ctrl
    env:
      STATE_RATE: "500"
      CAM_RATE: "30"
      HEADLESS: "False"
      STATE_BUFFER_SIZE: "200"
      CAM_BUFFER_SIZE: "8"
      SEN_TS: "False"
      CAMERA_TYPE: "empty"
      RATE_HZ: "500"

  - name: teleop_keyboard
    build: pip install hex_flow_node_teleop
    run: hex-flow-teleop-keyboard
    required: true
    hidden: true
    remap:
      teleop_keyboard: teleop_keyboard/teleop_keyboard
    env:
      DEVICE_PATH: ""

  - name: replay_archer_y6
    build: pip install hex_flow_replay_archer_y6
    run: hex-flow-replay-archer-y6
    required: true
    remap:
      arm_state: mujoco_archer_y6/arm_state
      grip_state: mujoco_archer_y6/grip_state
      arm_ctrl: mujoco_archer_y6/arm_ctrl
      grip_ctrl: mujoco_archer_y6/grip_ctrl
      keys: teleop_keyboard/teleop_keyboard
      record: replay_archer_y6/record
    env:
      RATE_HZ: "500"
      ARM_STABLE_POS: "0.0,-1.5,3.0,0.07,0.0,0.0"
      GRIP_STABLE_POS: "0.5"
      ARM_KP: "200.0,200.0,250.0,150.0,100.0,100.0"
      ARM_KD: "5.0,5.0,5.0,5.0,2.0,2.0"
      GRIP_KP: "10.0"
      GRIP_KD: "0.5"
      ARRIVE_THRESHOLD: "0.06"
      ARM_ERR_THRESHOLD: "0.04"
      GRIP_ERR_THRESHOLD: "0.02"
      MCAP_PATH: "/path/to/replay_data/episode_000001.mcap"
      LOOP_COUNT: "1"

  - name: data_record
    build: pip install hex_flow_node_data
    run: hex-flow-data-record
    required: false
    remap:
      arm_state: mujoco_archer_y6/arm_state
      grip_state: mujoco_archer_y6/grip_state
      record: replay_archer_y6/record
    env:
      RECORD_PATH: "/path/to/record_data"
      FOXGLOVE_HOST: "127.0.0.1"
      FOXGLOVE_PORT: "8765"
      START_CNT: "0"
```

# Message Types (FlatBuffer)

This node publishes and subscribes to FlatBuffer message types. All robot topics use FlatBuffer messages from `hex_util_msg.msg_robot`.

## Subscribed Topics

### `arm_state` — `HexArmState`

| Field       | Type      | Description                                   |
| ----------- | --------- | --------------------------------------------- |
| `ts_ns`     | `int64`   | Timestamp in nanoseconds                      |
| `jnt_pos`   | `float64` | Joint positions (rad)                         |
| `jnt_vel`   | `float64` | Joint velocities (rad/s)                      |
| `jnt_eff`   | `float64` | Joint efforts (Nm)                            |
| `pose_pos`  | `float64` | End-effector position (m)                     |
| `pose_quat` | `float64` | End-effector orientation (quaternion)         |

### `grip_state` — `HexGripState`

| Field     | Type      | Description                                   |
| --------- | --------- | --------------------------------------------- |
| `ts_ns`   | `int64`   | Timestamp in nanoseconds                      |
| `jnt_pos` | `float64` | Gripper joint position                        |
| `jnt_vel` | `float64` | Gripper joint velocity                        |
| `jnt_eff` | `float64` | Gripper joint effort                          |

### `keys` — `HexTeleopKeyboard`

| Field       | Type      | Description                              |
| ----------- | --------- | ---------------------------------------- |
| `ts_ns`     | `int64`   | Timestamp in nanoseconds                 |
| `action`    | `uint8`   | Action type (press / release)            |
| `key_q`     | `bool`    | Q key state                              |
| `key_w`     | `bool`    | W key state                              |
| ...         | `...`     | ...                                      |

> Full schema: [`msgs/msg_teleop/teleop_keyboard.fbs`](https://github.com/hexfellow/hex_util_msg/blob/main/msgs/msg_teleop/teleop_keyboard.fbs)

## Published Topics

### `arm_ctrl` — `HexArmCtrl`

| Field       | Type      | Description                                    |
| ----------- | --------- | ---------------------------------------------- |
| `ts_ns`     | `int64`   | Timestamp in nanoseconds                       |
| `ctrl_mode` | `uint8`   | Control mode enum (`pos` during init/exit/prep, `comp` during run) |
| `jnt_pos`   | `float64` | Target joint positions                         |
| `jnt_vel`   | `float64` | Target joint velocities                        |
| `mit_kp`    | `float64` | Stiffness gains                                |
| `mit_kd`    | `float64` | Damping gains                                  |
| `lim_err`   | `float64` | Position error limit for safety                |

### `grip_ctrl` — `HexGripCtrl`

| Field       | Type      | Description                                    |
| ----------- | --------- | ---------------------------------------------- |
| `ts_ns`     | `int64`   | Timestamp in nanoseconds                       |
| `ctrl_mode` | `uint8`   | Control mode enum (`pos` during init/exit/prep, `comp` during run) |
| `jnt_pos`   | `float64` | Target gripper position                        |
| `jnt_vel`   | `float64` | Target gripper velocity                        |
| `mit_kp`    | `float64` | Stiffness gains                                |
| `mit_kd`    | `float64` | Damping gains                                  |
| `lim_err`   | `float64` | Position error limit for safety                |

### `record` — `HexBool`

| Field   | Type      | Description                                    |
| ------- | --------- | ---------------------------------------------- |
| `ts_ns` | `int64`   | Timestamp in nanoseconds                       |
| `data`  | `bool`    | Record signal (`true` to start, `false` to stop) |

Schema: [`msgs/msg_robot/arm_ctrl.fbs`](https://github.com/hexfellow/hex_util_msg/blob/main/msgs/msg_robot/arm_ctrl.fbs) | [`msgs/msg_robot/grip_ctrl.fbs`](https://github.com/hexfellow/hex_util_msg/blob/main/msgs/msg_robot/grip_ctrl.fbs) | [`msgs/msg_basic/bool.fbs`](https://github.com/hexfellow/hex_util_msg/blob/main/msgs/msg_basic/bool.fbs)

# Environment Variables

## All Nodes

| Variable             | Type  | Default         | Description                                                |
| -------------------- | ----- | --------------- | ---------------------------------------------------------- |
| `HEX_FLOW_NODE_NAME` | `str` | constructor arg | Overrides node name (handled by `hex_flow_core`)           |
| `HEX_FLOW_REMAP`     | `str` | `{}`            | JSON dict for topic remapping (handled by `hex_flow_core`) |
| `RUST_LOG`           | `str` | `info`          | Log level for `envlog`                                     |

## Replay Node (`hex-flow-replay-archer-y6`)

| Variable             | Type    | Default                                          | Description                                         |
| -------------------- | ------- | ------------------------------------------------ | --------------------------------------------------- |
| `RATE_HZ`            | `float` | `10.0`                                           | Control loop rate in Hz                             |
| `ARM_STABLE_POS`     | `str`   | `"0.0,-1.5,3.0,0.07,0.0,0.0"`                   | Arm stable joint position (6-DOF comma-separated)   |
| `GRIP_STABLE_POS`    | `str`   | `"0.5"`                                          | Gripper stable position                             |
| `ARM_KP`             | `str`   | `"200.0,200.0,250.0,150.0,100.0,100.0"`          | Arm stiffness gains (6-DOF comma-separated)         |
| `ARM_KD`             | `str`   | `"5.0,5.0,5.0,5.0,2.0,2.0"`                     | Arm damping gains (6-DOF comma-separated)           |
| `GRIP_KP`            | `str`   | `"10.0"`                                          | Gripper stiffness gain                              |
| `GRIP_KD`            | `str`   | `"0.5"`                                           | Gripper damping gain                                |
| `ARRIVE_THRESHOLD`   | `float` | `0.06`                                           | Joint position threshold (rad) to consider arrived  |
| `ARM_ERR_THRESHOLD`  | `float` | `0.02`                                           | Arm position error limit for safety (`lim_err`)     |
| `GRIP_ERR_THRESHOLD` | `float` | `0.02`                                           | Gripper position error limit for safety (`lim_err`) |
| `MCAP_PATH`          | `str`   | *required*                                       | Path to the MCAP bag file to replay                 |
| `LOOP_COUNT`         | `int`   | `1`                                              | Number of times to replay the trajectory            |

> **Note**: When `MCAP_PATH` is not set or empty, the node skips bag loading and uses zero-vector trajectories. This is useful for testing the control flow without an actual bag file.

# Architecture

The replay node implements a four-phase lifecycle with integrated bag replay:

1. **Parameter construction** — reads environment variables and configures the node parameters: control rate, stable positions, PID gains, arrival/error thresholds, MCAP path, and loop count.

2. **Subscription setup** — subscribes to `arm_state`, `grip_state` (from the robot source), and `keys` (from the teleop keyboard node). It publishes `arm_ctrl`, `grip_ctrl`, and `record` topics.

3. **Init phase** — On `start()`, a teleop monitor thread begins polling the `keys` topic at 100 Hz. The main loop then enters the init phase, publishing position-mode (`HexArmCtrlMode.pos`) commands targeting the configured `arm_stable_pos` and `grip_stable_pos`. It waits until all joints are within `arrive_threshold` radians of the target.

4. **Work phase** — Once the robot has arrived at the stable position, the node transitions into the work loop, which consists of three sub-stages:
   - **Load**: Parses the MCAP bag file using `HexMcapReader`, extracting `arm_state` and `grip_state` time-series arrays. If no bag data is found, the node exits gracefully.
   - **Prep**: Drives the robot arm and gripper to the bag's starting joint positions using position-mode commands. Once the arm arrives within `arrive_threshold` and a short countdown elapses, a `record=True` signal is published to trigger external data recording (e.g., via `hex_flow_node_data`).
   - **Run**: Replays the trajectory by time-interpolating (`time_interp`) arm positions and velocities at each control cycle from the bag data. Commands are published in compensation mode (`HexArmCtrlMode.comp`) with the configured PID gains. When the bag end timestamp is reached, a `record=False` signal is published, and the loop increments (if `LOOP_COUNT > 1`, the prep+run sub-stages repeat).

5. **Exit phase** — When the `q` key is pressed (detected by the teleop thread) or `Ctrl+C` is received, the node publishes `record=False`, then re-enters the position-mode control loop, driving the arm back to `arm_stable_pos` / `grip_stable_pos` before stopping the node. This ensures a safe, repeatable shutdown.

This architecture decouples the replay logic from the underlying robot hardware interface — the node interacts solely through Zenoh topics, making it compatible with both real Archer Y6 hardware and MuJoCo simulation without code changes.

# 📄 License

Apache License 2.0. See [LICENSE](LICENSE).

# 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hexfellow/hex_flow_replay_archer_y6&type=Date)](https://star-history.com/#hexfellow/hex_flow_replay_archer_y6&Date)

# 👥 Contributors

<a href="https://github.com/hexfellow/hex_flow_replay_archer_y6/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=hexfellow/hex_flow_replay_archer_y6" />
</a>

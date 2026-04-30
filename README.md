<h1 align="center">HEX FLOW TEMPLATE ARCHER Y6</h1>

<p align="center">
    <a href="https://github.com/hexfellow/hex_flow_template_archer_y6/stargazers">
        <img src="https://img.shields.io/github/stars/hexfellow/hex_flow_template_archer_y6?style=flat-square&logo=github" />
    </a>
    <a href="https://github.com/hexfellow/hex_flow_template_archer_y6/forks">
        <img src="https://img.shields.io/github/forks/hexfellow/hex_flow_template_archer_y6?style=flat-square&logo=github" />
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/hexfellow/hex_flow_template_archer_y6/issues">
        <img src="https://img.shields.io/github/issues/hexfellow/hex_flow_template_archer_y6?style=flat-square&logo=github" />
    </a>
</p>

---

# 📖 Overview

## What is `hex_flow_template_archer_y6`

`hex_flow_template_archer_y6` provides a ready-to-use Archer Y6 control template built on the hex-flow framework. It orchestrates the Archer Y6 robot arm with a three-phase lifecycle — **init**, **work**, and **exit** — enabling seamless integration of real or simulated Archer Y6 hardware with keyboard teleoperation.

### Core lifecycle

1. **Init phase** — On startup, the template commands the arm and gripper to move to a configurable stable position, waiting until the robot arrives within a configurable error threshold.
2. **Work phase** — Once at the stable position, the template switches to **compensation mode**, publishing zero-torque compensation commands every control cycle, keeping the arm in a gravity-compensated state ready for manipulation.
3. **Exit phase** — On shutdown (triggered by pressing the `q` key or `Ctrl+C`), the template commands the arm back to the stable position before exiting cleanly.

## What problem it solves

- **Out-of-the-box control flow**: Provides a standard life cycle (init → work → exit) for Archer Y6, eliminating the need to write boilerplate state machine logic.
- **Graceful shutdown**: Handles both keyboard-triggered (`q` key) and signal-based (`Ctrl+C`) shutdown, automatically returning the arm to a safe stable position.
- **Flexible deployment**: Supports both real robot hardware (via `hex_flow_node_robot`) and MuJoCo simulation (via `hex_flow_node_mujoco`) — just swap the robot source with zero code changes to the template.
- **Keyboard teleop integration**: Subscribes to keyboard events via `hex_flow_node_teleop`, enabling a `q`-key shutdown mechanism.

## Target users

- Engineers deploying Archer Y6 robot arms in automated systems who need a quick-start control loop.
- Developers and researchers prototyping on Archer Y6 and transitioning from simulation to real hardware.
- Users of the hex-flow framework looking for a reference implementation of a robot control node.

## Nodes

| Node                              | Description                              | Publishes                 | Subscribes                          |
| --------------------------------- | ---------------------------------------- | ------------------------- | ----------------------------------- |
| `hex-flow-template-archer-y6`     | Archer Y6 control template               | `arm_ctrl`, `grip_ctrl`   | `arm_state`, `grip_state`, `keys`   |

## Architecture diagram

```
┌─────────────────┐     arm_state / grip_state      ┌─────────────────────────┐
│  Robot Source   │ ──────────────────────────────> │  hex-flow-template-     │
│ (real or MuJoCo)│                                 │  archer-y6              │
│                 │ <────────────────────────────── │                         │
└─────────────────┘     arm_ctrl / grip_ctrl        └─────────────────────────┘
                                                               ▲
                                                               │ keys
                                                               │
                                                      ┌────────┴────────┐
                                                      │ teleop_keyboard │
                                                      └─────────────────┘
```

The template sits between a robot source (either `hex-flow-robot-archer-y6` for real hardware or `hex-flow-mujoco-archer-y6` for MuJoCo simulation) and a teleop keyboard node. It subscribes to robot state topics and keyboard events, and publishes control commands back to the robot source.

# 📦 Installation

## Requirements

- **Python** >= 3.10
- **Core dependencies**:
  - `hex_flow_core` >= 0.0.0, < 0.1.0
  - `hex_flow_node_robot` >= 0.0.0, < 0.1.0
  - `hex_flow_node_teleop` >= 0.0.0, < 0.1.0
  - `hex_flow_node_mujoco` >= 0.0.0, < 0.1.0

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

## Install `hex-flow-template-archer-y6` from source

We provide a [venv.sh](venv.sh) script to create a virtual environment with all dependencies installed. However, you need to install uv first. For uv installation, please refer to `uv` official [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then you can use [venv.sh](venv.sh) to create a virtual environment with all dependencies installed:

```bash
git clone https://github.com/hexfellow/hex_flow_template_archer_y6.git
cd hex_flow_template_archer_y6
./venv.sh
```

# 📑 Python Config API

The package provides the `default_template_archer_y6_node` helper function that returns a `NodeConfig` object for easy integration into your `LaunchConfig`.

## Real robot launch

```python
from hex_flow_core import LaunchConfig
from hex_flow_node_robot import default_robot_archer_y6_node
from hex_flow_node_teleop import default_teleop_keyboard_node
from hex_flow_template_archer_y6 import default_template_archer_y6_node

config = LaunchConfig(
    local_only=True,
    enable_tui=True,
    log_to_file=True,
    save_path="/tmp/real_template.yml",
)

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
    "template_archer_y6":
    default_template_archer_y6_node(
        name="template_archer_y6",
        rate_hz=500.0,
        arm_stable_pos="0.0,-1.5,3.0,0.07,0.0,0.0",
        grip_stable_pos="0.5",
        arrive_threshold=0.06,
        err_threshold=0.02,
        required=True,
        hidden=False,
        remap_dict={
            "arm_state": "robot_archer_y6/arm_state",
            "grip_state": "robot_archer_y6/grip_state",
            "arm_ctrl": "robot_archer_y6/arm_ctrl",
            "grip_ctrl": "robot_archer_y6/grip_ctrl",
            "keys": "teleop_keyboard/teleop_keyboard",
        },
    ),
}

config.set_nodes(nodes)
print(config.export())
```

## MuJoCo simulation launch

```python
from hex_flow_core import LaunchConfig
from hex_flow_node_mujoco import default_mujoco_archer_y6_node
from hex_flow_node_teleop import default_teleop_keyboard_node
from hex_flow_template_archer_y6 import default_template_archer_y6_node

config = LaunchConfig(
    local_only=True,
    enable_tui=True,
    log_to_file=True,
    save_path="/tmp/sim_template.yml",
)

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
    "template_archer_y6":
    default_template_archer_y6_node(
        name="template_archer_y6",
        rate_hz=500.0,
        arm_stable_pos="0.0,-1.5,3.0,0.07,0.0,0.0",
        grip_stable_pos="0.5",
        arrive_threshold=0.06,
        err_threshold=0.02,
        required=True,
        hidden=False,
        remap_dict={
            "arm_state": "mujoco_archer_y6/arm_state",
            "grip_state": "mujoco_archer_y6/grip_state",
            "arm_ctrl": "mujoco_archer_y6/arm_ctrl",
            "grip_ctrl": "mujoco_archer_y6/grip_ctrl",
            "keys": "teleop_keyboard/teleop_keyboard",
        },
    ),
}

config.set_nodes(nodes)
print(config.export())
```

### `default_template_archer_y6_node`

| Parameter          | Type    | Default                                          | Description                                         |
| ------------------ | ------- | ------------------------------------------------ | --------------------------------------------------- |
| `name`             | `str`   | `"template_archer_y6"`                           | Node name and remap prefix                          |
| `rate_hz`          | `float` | `500.0`                                          | Control loop rate in Hz                             |
| `arm_stable_pos`   | `str`   | `"0.0,-1.5,3.0,0.07,0.0,0.0"`                   | Arm stable joint position (6-DOF comma-separated)   |
| `grip_stable_pos`  | `str`   | `"0.5"`                                          | Gripper stable position                             |
| `arm_kp`           | `str`   | `"200.0,200.0,250.0,150.0,100.0,100.0"`          | Arm stiffness gains (6-DOF comma-separated)         |
| `arm_kd`           | `str`   | `"5.0,5.0,5.0,5.0,2.0,2.0"`                     | Arm damping gains (6-DOF comma-separated)           |
| `grip_kp`          | `str`   | `"10.0"`                                          | Gripper stiffness gain                              |
| `grip_kd`          | `str`   | `"0.5"`                                           | Gripper damping gain                                |
| `arrive_threshold` | `float` | `0.06`                                           | Joint position threshold (rad) to consider arrived  |
| `err_threshold`    | `float` | `0.02`                                           | Position error limit for safety (lim_err)           |
| `required`         | `bool`  | `True`                                           | Required for launch                                 |
| `hidden`           | `bool`  | `False`                                          | Hidden node                                         |
| `remap_dict`       | `dict`  | `None`                                           | Custom remap; defaults to `{robot_source}/*`        |
| `robot_source`     | `str`   | `"mujoco_archer_y6"`                             | Robot node to subscribe/publish to                  |
| `keys_source`      | `str`   | `"teleop_keyboard"`                              | Teleop keyboard node to subscribe to                |

# 💡 Examples

Ready-to-run config scripts are provided in the [`example/`](example/) directory. Each script prints a launch YAML to stdout, intended for use with `hexflow run`:

### Real robot

```bash
# 500 Hz control loop with real Archer Y6 hardware
hexflow run example/real_template.launch.py
```

### MuJoCo simulation

```bash
# 500 Hz control loop with MuJoCo simulated Archer Y6
hexflow run example/sim_template.launch.py
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

  - name: template_archer_y6
    build: pip install hex_flow_template_archer_y6
    run: hex-flow-template-archer-y6
    required: true
    remap:
      arm_state: robot_archer_y6/arm_state
      grip_state: robot_archer_y6/grip_state
      arm_ctrl: robot_archer_y6/arm_ctrl
      grip_ctrl: robot_archer_y6/grip_ctrl
      keys: teleop_keyboard/teleop_keyboard
    env:
      RATE_HZ: "500"
      ARM_STABLE_POS: "0.0,-1.5,3.0,0.07,0.0,0.0"
      GRIP_STABLE_POS: "0.5"
      ARM_KP: "200.0,200.0,250.0,150.0,100.0,100.0"
      ARM_KD: "5.0,5.0,5.0,5.0,2.0,2.0"
      GRIP_KP: "10.0"
      GRIP_KD: "0.5"
      ARRIVE_THRESHOLD: "0.06"
      ERR_THRESHOLD: "0.02"
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

  - name: template_archer_y6
    build: pip install hex_flow_template_archer_y6
    run: hex-flow-template-archer-y6
    required: true
    remap:
      arm_state: mujoco_archer_y6/arm_state
      grip_state: mujoco_archer_y6/grip_state
      arm_ctrl: mujoco_archer_y6/arm_ctrl
      grip_ctrl: mujoco_archer_y6/grip_ctrl
      keys: teleop_keyboard/teleop_keyboard
    env:
      RATE_HZ: "500"
      ARM_STABLE_POS: "0.0,-1.5,3.0,0.07,0.0,0.0"
      GRIP_STABLE_POS: "0.5"
      ARM_KP: "200.0,200.0,250.0,150.0,100.0,100.0"
      ARM_KD: "5.0,5.0,5.0,5.0,2.0,2.0"
      GRIP_KP: "10.0"
      GRIP_KD: "0.5"
      ARRIVE_THRESHOLD: "0.06"
      ERR_THRESHOLD: "0.02"
```

# Message Types (FlatBuffer)

This template publishes and subscribes to the same FlatBuffer message types as the Archer Y6 robot driver from `hex_flow_node_robot`. All topics use FlatBuffer messages from `hex_util_msg.msg_robot`.

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
| `ctrl_mode` | `uint8`   | Control mode enum (`pos` during init/exit, `comp` during work) |
| `jnt_pos`   | `float64` | Target joint positions                         |
| `jnt_vel`   | `float64` | Target joint velocities                        |
| `mit_kp`    | `float64` | Stiffness gains                                |
| `mit_kd`    | `float64` | Damping gains                                  |
| `lim_err`   | `float64` | Position error limit for safety                |

### `grip_ctrl` — `HexGripCtrl`

| Field       | Type      | Description                                    |
| ----------- | --------- | ---------------------------------------------- |
| `ts_ns`     | `int64`   | Timestamp in nanoseconds                       |
| `ctrl_mode` | `uint8`   | Control mode enum (`pos` during init/exit, `comp` during work) |
| `jnt_pos`   | `float64` | Target gripper position                        |
| `jnt_vel`   | `float64` | Target gripper velocity                        |
| `mit_kp`    | `float64` | Stiffness gains                                |
| `mit_kd`    | `float64` | Damping gains                                  |
| `lim_err`   | `float64` | Position error limit for safety                |

Schema: [`msgs/msg_robot/arm_ctrl.fbs`](https://github.com/hexfellow/hex_util_msg/blob/main/msgs/msg_robot/arm_ctrl.fbs) | [`msgs/msg_robot/grip_ctrl.fbs`](https://github.com/hexfellow/hex_util_msg/blob/main/msgs/msg_robot/grip_ctrl.fbs)

# Environment Variables

## All Nodes

| Variable             | Type  | Default         | Description                                                |
| -------------------- | ----- | --------------- | ---------------------------------------------------------- |
| `HEX_FLOW_NODE_NAME` | `str` | constructor arg | Overrides node name (handled by `hex_flow_core`)           |
| `HEX_FLOW_REMAP`     | `str` | `{}`            | JSON dict for topic remapping (handled by `hex_flow_core`) |
| `RUST_LOG`           | `str` | `info`          | Log level for `envlog`                                     |

## Template Node (`hex-flow-template-archer-y6`)

| Variable           | Type    | Default                                          | Description                                         |
| ------------------ | ------- | ------------------------------------------------ | --------------------------------------------------- |
| `RATE_HZ`          | `float` | `500.0`                                          | Control loop rate in Hz                             |
| `ARM_STABLE_POS`   | `str`   | `"0.0,-1.5,3.0,0.07,0.0,0.0"`                   | Arm stable joint position (6-DOF comma-separated)   |
| `GRIP_STABLE_POS`  | `str`   | `"0.5"`                                          | Gripper stable position                             |
| `ARM_KP`           | `str`   | `"200.0,200.0,250.0,150.0,100.0,100.0"`          | Arm stiffness gains (6-DOF comma-separated)         |
| `ARM_KD`           | `str`   | `"5.0,5.0,5.0,5.0,2.0,2.0"`                     | Arm damping gains (6-DOF comma-separated)           |
| `GRIP_KP`          | `str`   | `"10.0"`                                          | Gripper stiffness gain                              |
| `GRIP_KD`          | `str`   | `"0.5"`                                           | Gripper damping gain                                |
| `ARRIVE_THRESHOLD` | `float` | `0.06`                                           | Joint position threshold (rad) to consider arrived  |
| `ERR_THRESHOLD`    | `float` | `0.02`                                           | Position error limit for safety (`lim_err`)         |

# Architecture

The template node implements a three-phase lifecycle:

1. **Parameter construction** — reads environment variables and configures the template parameters: control rate, stable positions, PID gains, and arrival/error thresholds.

2. **Subscription setup** — subscribes to `arm_state`, `grip_state` (from the robot source), and `keys` (from the teleop keyboard node). It publishes `arm_ctrl` and `grip_ctrl` commands back to the robot source.

3. **Init phase** — On `start()`, a teleop monitor thread begins polling the `keys` topic at 100 Hz. The main loop then enters the init phase, publishing position-mode (`HexArmCtrlMode.pos`) commands targeting the configured `arm_stable_pos` and `grip_stable_pos`. It waits until all joints are within `arrive_threshold` radians of the target.

4. **Work phase** — Once the robot has arrived at the stable position, the template switches to compensation mode (`HexArmCtrlMode.comp`), publishing zero-vector commands each cycle. This keeps the arm in a gravity-compensated, freely movable state.

5. **Exit phase** — When the `q` key is pressed (detected by the teleop thread) or `Ctrl+C` is received, the template re-enters the position-mode control loop, driving the arm back to `arm_stable_pos` / `grip_stable_pos` before stopping the node. This ensures a safe, repeatable shutdown.

This architecture decouples the template's lifecycle logic from the underlying robot hardware interface — the template interacts solely through Zenoh topics, making it compatible with both real Archer Y6 hardware and MuJoCo simulation without code changes.

# 📄 License

Apache License 2.0. See [LICENSE](LICENSE).

# 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hexfellow/hex_flow_template_archer_y6&type=Date)](https://star-history.com/#hexfellow/hex_flow_template_archer_y6&Date)

# 👥 Contributors

<a href="https://github.com/hexfellow/hex_flow_template_archer_y6/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=hexfellow/hex_flow_template_archer_y6" />
</a>

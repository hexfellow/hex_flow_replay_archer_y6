#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-27
################################################################

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
    save_path="/tmp/real_template.yml",
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD_PATH = f"{SCRIPT_DIR}/record_data"
REPLAY_DIR = f"{SCRIPT_DIR}/replay_data"

nodes = {
    "robot_archer_y6":
    default_robot_archer_y6_node(
        name="robot_archer_y6",
        # host="172.18.23.197",
        # port=8439,
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
        mcap_path=f"{REPLAY_DIR}/episode_000001.mcap",
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
        record_path=RECORD_PATH,
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

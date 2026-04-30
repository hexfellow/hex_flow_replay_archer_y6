#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-28
################################################################

from hex_flow_core import NodeConfig

_BUILD_CMD = "pip install hex_flow_replay_archer_y6"

# ──────────────────────────────────────────────────────────────
#  Comp Control
# ──────────────────────────────────────────────────────────────


def default_replay_archer_y6_node(
    name: str = "replay_archer_y6",
    rate_hz: float = 500.0,
    arm_stable_pos: str = "0.0,-1.5,3.0,0.07,0.0,0.0",
    grip_stable_pos: str = "0.5",
    arm_kp: str = "200.0,200.0,250.0,150.0,100.0,100.0",
    arm_kd: str = "5.0,5.0,5.0,5.0,2.0,2.0",
    grip_kp: str = "10.0",
    grip_kd: str = "0.5",
    arrive_threshold: float = 0.06,
    arm_err_threshold: float = 0.02,
    grip_err_threshold: float = 0.02,
    mcap_path: str = "",
    loop_count: int = 1,
    required: bool = True,
    hidden: bool = False,
    remap_dict: dict[str, str] | None = None,
    robot_source: str = "mujoco_archer_y6",
    keys_source: str = "teleop_keyboard",
) -> NodeConfig:
    if remap_dict is None:
        remap_dict = {
            "arm_state": f"{robot_source}/arm_state",
            "grip_state": f"{robot_source}/grip_state",
            "arm_ctrl": f"{robot_source}/arm_ctrl",
            "grip_ctrl": f"{robot_source}/grip_ctrl",
            "keys": f"{keys_source}/teleop_keyboard",
        }

    return NodeConfig(
        name=name,
        build_cmd=_BUILD_CMD,
        run_cmd="hex-flow-replay-archer-y6",
        required=required,
        hidden=hidden,
        remap_dict=remap_dict,
        env_dict={
            "RATE_HZ": str(rate_hz),
            "ARM_STABLE_POS": arm_stable_pos,
            "GRIP_STABLE_POS": grip_stable_pos,
            "ARRIVE_THRESHOLD": str(arrive_threshold),
            "ARM_ERR_THRESHOLD": str(arm_err_threshold),
            "GRIP_ERR_THRESHOLD": str(grip_err_threshold),
            "ARM_KP": arm_kp,
            "ARM_KD": arm_kd,
            "GRIP_KP": grip_kp,
            "GRIP_KD": grip_kd,
            "MCAP_PATH": mcap_path,
            "LOOP_COUNT": str(loop_count),
        },
    )

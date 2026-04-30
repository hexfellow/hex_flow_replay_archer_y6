#!/usr/bin/env python3
# -*- coding:utf-8 -*-
################################################################
# Copyright 2026 Dong Zhaorui. All rights reserved.
# Author: Dong Zhaorui 847235539@qq.com
# Date  : 2026-04-28
################################################################

import traceback
import threading
import numpy as np
from hex_flow_core import Node
from hex_util_runtime import (HexRate, get_env_float, get_env_int,
                              get_env_ndarray, get_env_str, ns_now)
from hex_util_msg.msg_robot.HexArmCtrlMode import HexArmCtrlMode
from hex_util_msg.msg_robot.HexGripCtrlMode import HexGripCtrlMode
from hex_util_msg.builder_robot import (build_hex_arm_ctrl,
                                        build_hex_grip_ctrl,
                                        parse_hex_arm_state,
                                        parse_hex_grip_state)
from hex_util_msg.builder_teleop import parse_hex_teleop_keyboard
from hex_util_msg.builder_basic import build_hex_bool
from hex_util_data import HexMcapReader
from hex_util_robot import time_interp


class HexFlowReplayArcherY6:

    def __init__(self, name: str = "replay_archer_y6"):
        self.__name = name
        self.__node = Node(self.__name)
        self.__node.start()
        self.__init_params()
        self.__init_vars()
        self.__init_subs()
        self.__init_pubs()
        self.__init_threads()

    def __init_params(self):
        self.__rate_hz = get_env_float("RATE_HZ", 10.0)
        self.__arm_stable_pos = get_env_ndarray("ARM_STABLE_POS",
                                                "0.0,-1.5,3.0,0.07,0.0,0.0")
        self.__grip_stable_pos = get_env_ndarray("GRIP_STABLE_POS", "0.5")
        self.__arm_kp = get_env_ndarray("ARM_KP",
                                        "200.0,200.0,250.0,150.0,100.0,100.0")
        self.__arm_kd = get_env_ndarray("ARM_KD", "5.0,5.0,5.0,5.0,2.0,2.0")
        self.__grip_kp = get_env_ndarray("GRIP_KP", "10.0")
        self.__grip_kd = get_env_ndarray("GRIP_KD", "0.5")
        self.__arrive_threshold = get_env_float("ARRIVE_THRESHOLD", 0.06)
        self.__arm_err_threshold = get_env_float("ARM_ERR_THRESHOLD", 0.02)
        self.__grip_err_threshold = get_env_float("GRIP_ERR_THRESHOLD", 0.02)
        self.__mcap_path = get_env_str("MCAP_PATH")
        self.__max_loops = get_env_int("LOOP_COUNT", 1)

    def __init_vars(self):
        self.__loop_count = 0
        self.__arm_ts_arr = np.zeros(0)
        self.__arm_pos_arr = np.zeros(0)
        self.__arm_vel_arr = np.zeros(0)
        self.__grip_ts_arr = np.zeros(0)
        self.__grip_pos_arr = np.zeros(0)
        self.__grip_vel_arr = np.zeros(0)
        self.__bag_start_ts = 0.0
        self.__bag_end_ts = 0.0
        self.__arm_bag_start_pos = np.zeros(6)
        self.__grip_bag_start_pos = np.zeros(1)
        self.__has_grip_data = False

    def __init_pubs(self):
        self.__node.create_pub("arm_ctrl")
        self.__node.create_pub("grip_ctrl")
        self.__node.create_pub("record")

    def __init_subs(self):
        self.__node.create_sub("arm_state")
        self.__node.create_sub("grip_state")
        self.__node.create_sub("keys")

    def __init_threads(self):
        self.__stop_event = threading.Event()
        self.__teleop_thread = threading.Thread(target=self.__teleop_process)

    def __is_running(self):
        return self.__node.is_working() and not self.__stop_event.is_set()

    def start(self):
        self.__stop_event.clear()
        self.__teleop_thread.start()
        self.__init_process()

    def run(self):
        try:
            self.__work_process()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
        finally:
            self.stop()

    def stop(self):
        self.__stop_event.set()
        self.__teleop_thread.join()
        self.__exit_process()
        self.__node.stop()

    ##############################################################
    # Work Related Functions
    ##############################################################
    def __teleop_process(self):
        prev_q = 0
        rate = HexRate(100.0)
        while self.__is_running():
            rate.sleep()

            data = self.__node.get("keys")
            if data is None:
                continue

            keys = parse_hex_teleop_keyboard(data)
            curr_q = keys["key_q"]
            if curr_q and not prev_q:
                self.__node.info(f"[{self.__name}]: Stop and exit")
                self.__stop_event.set()
            prev_q = curr_q

    def __init_process(self):
        try:
            self.__node.info(f"[{self.__name}]: move to init position")
            rate = HexRate(self.__rate_hz)
            while self.__node.is_working():
                rate.sleep()

                data = self.__node.get("arm_state", latest=True)
                if data is not None:
                    state = parse_hex_arm_state(data)
                    err = self.__arm_stable_pos - state["jnt_pos"]
                    if np.fabs(err).max() < self.__arrive_threshold:
                        break
                    self.__node.pub(
                        "arm_ctrl",
                        build_hex_arm_ctrl(
                            ts_ns=ns_now(),
                            ctrl_mode=HexArmCtrlMode.pos,
                            jnt_pos=self.__arm_stable_pos,
                            mit_kp=self.__arm_kp,
                            mit_kd=self.__arm_kd,
                            lim_err=self.__arm_err_threshold,
                        ),
                    )
                    self.__node.pub(
                        "grip_ctrl",
                        build_hex_grip_ctrl(
                            ts_ns=ns_now(),
                            ctrl_mode=HexGripCtrlMode.pos,
                            jnt_pos=self.__grip_stable_pos,
                            mit_kp=self.__grip_kp,
                            mit_kd=self.__grip_kd,
                            lim_err=self.__grip_err_threshold,
                        ),
                    )
        except Exception:
            traceback.print_exc()

    def __exit_process(self):
        try:
            self.__node.pub("record", build_hex_bool(ts_ns=ns_now(),
                                                     data=False))
            self.__node.info(f"[{self.__name}]: move to exit position")
            rate = HexRate(self.__rate_hz)
            while self.__node.is_working():
                rate.sleep()

                data = self.__node.get("arm_state", latest=True)
                if data is not None:
                    state = parse_hex_arm_state(data)
                    err = self.__arm_stable_pos - state["jnt_pos"]
                    if np.fabs(err).max() < self.__arrive_threshold:
                        break
                    self.__node.pub(
                        "arm_ctrl",
                        build_hex_arm_ctrl(
                            ts_ns=ns_now(),
                            ctrl_mode=HexArmCtrlMode.pos,
                            jnt_pos=self.__arm_stable_pos,
                            mit_kp=self.__arm_kp,
                            mit_kd=self.__arm_kd,
                            lim_err=self.__arm_err_threshold,
                        ),
                    )
                    self.__node.pub(
                        "grip_ctrl",
                        build_hex_grip_ctrl(
                            ts_ns=ns_now(),
                            ctrl_mode=HexGripCtrlMode.pos,
                            jnt_pos=self.__grip_stable_pos,
                            mit_kp=self.__grip_kp,
                            mit_kd=self.__grip_kd,
                            lim_err=self.__grip_err_threshold,
                        ),
                    )
        except Exception:
            traceback.print_exc()

    def __work_process(self):
        self.__node.info(f"[{self.__name}]: Start replay")
        if not self.__load_bag():
            self.__node.info(f"[{self.__name}]: Failed to load bag, exiting")
            self.__stop_event.set()
            return

        while self.__is_running() and self.__loop_count < self.__max_loops:
            self.__node.info(
                f"[{self.__name}]: Loop {self.__loop_count + 1}/{self.__max_loops}"
            )

            if not self.__prep_process():
                break
            if not self.__run_process():
                break

            self.__loop_count += 1
            self.__node.info(
                f"[{self.__name}]: [Judge] loop {self.__loop_count}/{self.__max_loops} completed"
            )

        if self.__is_running():
            self.__node.info(f"[{self.__name}]: All loops complete, exiting")
            self.__stop_event.set()

    # ------------------------------------------------------------------
    # Bag loading
    # ------------------------------------------------------------------

    def __load_bag(self) -> bool:
        if not self.__mcap_path:
            self.__node.info(
                f"[{self.__name}]: MCAP_PATH env var not set, using zeros")
            self.__arm_bag_start_pos = np.zeros(6)
            self.__grip_bag_start_pos = np.zeros(1)
            return True

        self.__node.info(f"[{self.__name}]: Loading bag: {self.__mcap_path}")
        reader = HexMcapReader(self.__mcap_path)

        # Find arm_state
        arm_data = reader.get_data("arm_state")
        if not arm_data:
            self.__node.info(f"[{self.__name}]: No arm_state data in bag")
            return False

        self.__arm_ts_arr = np.array([d["ts_ns"] for d in arm_data])
        self.__arm_pos_arr = np.array([d["jnt_pos"] for d in arm_data])
        self.__arm_vel_arr = np.array([d["jnt_vel"] for d in arm_data])

        self.__bag_start_ts = self.__arm_ts_arr[0]
        self.__bag_end_ts = self.__arm_ts_arr[-1]
        self.__arm_bag_start_pos = self.__arm_pos_arr[0].copy()

        self.__node.info(
            f"[{self.__name}]: Arm data loaded: "
            f"{len(arm_data)} msgs, "
            f"duration={(self.__bag_end_ts - self.__bag_start_ts)*1e-9:.3f}s")

        # Find grip_state
        grip_data = reader.get_data("grip_state")
        if grip_data:
            self.__grip_ts_arr = np.array([d["ts_ns"] for d in grip_data])
            self.__grip_pos_arr = np.array([d["jnt_pos"] for d in grip_data])
            self.__grip_vel_arr = np.array([d["jnt_vel"] for d in grip_data])
            self.__grip_bag_start_pos = self.__grip_pos_arr[0].copy()
            self.__has_grip_data = True
            self.__node.info(
                f"[{self.__name}]: Grip data loaded: "
                f"{len(grip_data)} msgs, "
                f"duration={(self.__bag_end_ts - self.__bag_start_ts)*1e-9:.3f}s"
            )
        else:
            self.__node.info(f"[{self.__name}]: No grip_state data in bag")

        return True

    # ------------------------------------------------------------------
    # Stage 1: Preparation
    # ------------------------------------------------------------------

    def __prep_process(self) -> bool:
        self.__node.info(
            f"[{self.__name}]: [Prep] moving to bag start position")
        rate = HexRate(self.__rate_hz)
        record_sended = False
        count_record = int(self.__rate_hz)
        count_run = int(self.__rate_hz * 1.1)

        while self.__is_running():
            rate.sleep()
            self.__node.pub(
                "arm_ctrl",
                build_hex_arm_ctrl(
                    ts_ns=ns_now(),
                    ctrl_mode=HexArmCtrlMode.pos,
                    jnt_pos=self.__arm_bag_start_pos,
                    mit_kp=self.__arm_kp,
                    mit_kd=self.__arm_kd,
                    lim_err=self.__arm_err_threshold,
                ),
            )
            self.__node.pub(
                "grip_ctrl",
                build_hex_grip_ctrl(
                    ts_ns=ns_now(),
                    ctrl_mode=HexGripCtrlMode.pos,
                    jnt_pos=self.__grip_bag_start_pos,
                    mit_kp=self.__grip_kp,
                    mit_kd=self.__grip_kd,
                    lim_err=self.__grip_err_threshold,
                ),
            )

            data = self.__node.get("arm_state", latest=True)
            if data is None:
                continue

            state = parse_hex_arm_state(data)
            err = self.__arm_bag_start_pos - state["jnt_pos"]
            arrive_flag = np.fabs(err).max() < self.__arrive_threshold

            if arrive_flag:
                count_record -= 1
                count_run -= 1

                if count_record <= 0 and not record_sended:
                    record_sended = True
                    self.__node.pub("record",
                                    build_hex_bool(ts_ns=ns_now(), data=True))

                if count_run <= 0:
                    self.__node.info(
                        f"[{self.__name}]: [Prep] countdown complete")
                    break

        return self.__is_running()

    # ------------------------------------------------------------------
    # Stage 2: Running
    # ------------------------------------------------------------------

    def __run_process(self) -> bool:
        self.__node.info(f"[{self.__name}]: [Run] replaying bag")
        rate = HexRate(self.__rate_hz)

        bag_duration = self.__bag_end_ts - self.__bag_start_ts
        start_ts = ns_now()
        while self.__is_running():
            rate.sleep()
            elapsed = ns_now() - start_ts
            search_ts = self.__bag_start_ts + elapsed

            if search_ts > self.__bag_end_ts:
                self.__node.pub("record",
                                build_hex_bool(ts_ns=ns_now(), data=False))
                self.__node.info(
                    f"[{self.__name}]: [Run] replay complete "
                    f"(elapsed={elapsed:.3f}s, bag={bag_duration:.3f}s)")
                break

            arm_pos = time_interp(search_ts, self.__arm_ts_arr,
                                  self.__arm_pos_arr).reshape(-1)
            arm_vel = time_interp(search_ts, self.__arm_ts_arr,
                                  self.__arm_vel_arr).reshape(-1)
            self.__node.pub(
                "arm_ctrl",
                build_hex_arm_ctrl(
                    ts_ns=ns_now(),
                    ctrl_mode=HexArmCtrlMode.comp,
                    jnt_pos=arm_pos,
                    jnt_vel=arm_vel,
                    mit_kp=self.__arm_kp,
                    mit_kd=self.__arm_kd,
                ),
            )

            grip_pos = time_interp(search_ts, self.__grip_ts_arr,
                                   self.__grip_pos_arr).reshape(-1)
            self.__node.pub(
                "grip_ctrl",
                build_hex_grip_ctrl(
                    ts_ns=ns_now(),
                    ctrl_mode=HexGripCtrlMode.comp,
                    jnt_pos=grip_pos,
                    jnt_vel=np.zeros(1),
                    mit_kp=self.__grip_kp,
                    mit_kd=self.__grip_kd,
                ),
            )

        return self.__is_running()

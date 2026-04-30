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
from hex_util_runtime import HexRate, get_env_float, get_env_ndarray, ns_now
from hex_util_msg.msg_robot.HexArmCtrlMode import HexArmCtrlMode
from hex_util_msg.msg_robot.HexGripCtrlMode import HexGripCtrlMode
from hex_util_msg.builder_robot import (build_hex_arm_ctrl,
                                        build_hex_grip_ctrl,
                                        parse_hex_arm_state)
from hex_util_msg.builder_teleop import parse_hex_teleop_keyboard


class HexFlowTemplateArcherY6:

    def __init__(self, name: str = "template_archer_y6"):
        self.__name = name
        self.__node = Node(self.__name)
        self.__node.start()
        self.__init_params()
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

    def __init_pubs(self):
        self.__node.create_pub("arm_ctrl")
        self.__node.create_pub("grip_ctrl")

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
        self.__node.info(f"[{self.__name}]: Start")
        rate = HexRate(self.__rate_hz)
        while self.__is_running():
            rate.sleep()

            self.__node.pub(
                "arm_ctrl",
                build_hex_arm_ctrl(
                    ts_ns=ns_now(),
                    ctrl_mode=HexArmCtrlMode.comp,
                    jnt_pos=np.zeros(6),
                    jnt_vel=np.zeros(6),
                    mit_tau=np.zeros(6),
                    mit_kp=np.zeros(6),
                    mit_kd=np.zeros(6),
                ),
            )
            self.__node.pub(
                "grip_ctrl",
                build_hex_grip_ctrl(
                    ts_ns=ns_now(),
                    ctrl_mode=HexGripCtrlMode.comp,
                    jnt_pos=np.zeros(1),
                    jnt_vel=np.zeros(1),
                    mit_tau=np.zeros(1),
                    mit_kp=np.zeros(1),
                    mit_kd=np.zeros(1),
                ),
            )

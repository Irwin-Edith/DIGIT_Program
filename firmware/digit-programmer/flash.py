# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.
import os
import sys

import logging
import subprocess

from omegaconf import OmegaConf

from usb.core import find as find_device

DIGIT_SERIAL_MASK = "DXXXXX".encode("utf-16le")
DIGIT_SERIAL_ID_LENGTH = 5
DFU_UTIL_CMD = "dfu-util"
DFU_TMP_BIN = "digit_firmware_tmp.bin"

_log = logging.getLogger("DigitProgrammer")
logging.basicConfig(level=logging.DEBUG)


def format_serial(serial):
    '''
    Format the serial number to be 5 digits long, with leading zeros if necessary.
    它将用户提供的序列号转换为特定格式（以 "D" 开头，长度为 5 个字符，不足部分用 "0" 填充），并将其编码为 UTF-16LE 格式。
    它会检查固件文件中是否包含一个特定的序列号占位符（DIGIT_SERIAL_MASK，即 "DXXXXX" 的 UTF-16LE 编码）。
    如果找到占位符，就将其替换为新的序列号，并生成一个临时的固件文件（digit_firmware_tmp.bin）。
    这个功能通常用于在设备固件中嵌入唯一的序列号。
    '''
    if not serial.isdigit() or len(serial) > DIGIT_SERIAL_ID_LENGTH:
        _log.error("Serial must be between 1 and 5 characters long.")
        sys.exit(1)
    serial = "D{}".format(serial.rjust(DIGIT_SERIAL_ID_LENGTH, "0"))
    serial = serial.encode("utf-16le")
    return serial


def set_serial(firmware_bin, serial):
    '''
    Set the serial number in the firmware binary.
    将格式化后的序列号写入到指定的固件文件中。
    '''
    _log.info(f"Attempting to find DIGIT serial mask in {firmware_bin} binary.")
    with open(firmware_bin, "rb") as firmware_f:
        firmware_data = firmware_f.read()
    if firmware_data.find(DIGIT_SERIAL_MASK) < 0:
        _log.error("Could not find serial pattern in firmware!")
        sys.exit(1)
    _log.info("Found serial pattern...")
    firmware_data = firmware_data.replace(DIGIT_SERIAL_MASK, serial)
    with open(DFU_TMP_BIN, "w+b") as firmware_tmp:
        firmware_tmp.write(firmware_data)
    _log.info("Serial number written to new firmware binary.")


def find_digit_usb_dev(id_vendor, id_product):
    dev = find_device(idVendor=id_vendor, idProduct=id_product)
    return dev


def reset_device(usb_dev):
    usb_dev.reset()


def program_digit():
    cwd = os.path.dirname(os.path.realpath(__file__))
    dfu_util_args = [DFU_UTIL_CMD, "-vRD", DFU_TMP_BIN]
    subprocess.run(dfu_util_args, cwd=cwd)


def main():
    cli_conf = OmegaConf.from_cli()
    base_conf = OmegaConf.load("programmer.yaml")
    conf = OmegaConf.merge(base_conf, cli_conf)
    _log.info(f"DIGIT programmer config: {conf}")

    full_serial = format_serial(str(conf.digit.serial))
    set_serial(conf.digit.firmware, full_serial)

    _log.info("Flashing DIGIT firmware...")
    input("Unplug and plug DIGIT into usb then press ENTER...")
    program_digit()
    _log.info("Finished flashing firmware to DIGIT!")


if __name__ == "__main__":
    sys.exit(main())

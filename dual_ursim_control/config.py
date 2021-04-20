import os

class Config:
    MASTER_IP = os.environ.get("MASTER_IP")
    SLAVE_IP = os.environ.get("SLAVE_IP")

    MASTER_GRIPPER_WIDTH_OPENED = int(os.environ.get("MASTER_GRIPPER_WIDTH_OPENED"))
    MASTER_GRIPPER_WIDTH_CLOSED = int(os.environ.get("MASTER_GRIPPER_WIDTH_CLOSED"))

    SLAVE_GRIPPER_IP = os.environ.get("SLAVE_GRIPPER_IP")
    SLAVE_GRIPPER_WIDTH_OPENED = int(os.environ.get("SLAVE_GRIPPER_WIDTH_OPENED"))
    SLAVE_GRIPPER_WIDTH_CLOSED = int(os.environ.get("SLAVE_GRIPPER_WIDTH_CLOSED"))

    MASTER_ENABLE = os.environ.get("MASTER_ENABLE", 'False').lower() in ('true', '1', 't')
    SLAVE_ENABLE = os.environ.get("SLAVE_ENABLE", 'False').lower() in ('true', '1', 't')

    JOGGING_ENABLE = os.environ.get("JOGGING_ENABLE", 'False').lower() in ('true', '1', 't')

    # SLOW / FAST
    EXECUTION = os.environ.get("EXECUTION")

    L_SPEED_SLOW = float(os.environ.get("L_SPEED_SLOW"))
    L_SPEED_FAST = float(os.environ.get("L_SPEED_FAST"))
    L_ACC_SLOW = float(os.environ.get("L_ACC_SLOW"))
    L_ACC_FAST = float(os.environ.get("L_ACC_FAST"))

    J_SPEED_SLOW = float(os.environ.get("J_SPEED_SLOW"))
    J_SPEED_FAST = float(os.environ.get("J_SPEED_FAST"))
    J_ACC_SLOW = float(os.environ.get("J_ACC_SLOW"))
    J_ACC_FAST = float(os.environ.get("J_ACC_FAST"))
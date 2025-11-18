from enum import Enum
from time import sleep
from message import MessageType
from logger import robot_log, warning_log, error_log


class RobotState(Enum):
    IDLE = "IDLE"
    MOVING_TO_WAITING = "MOVING_TO_WAITING"
    AT_WAITING_POSITION = "AT_WAITING_POSITION"
    MOVING_TO_LOADING = "MOVING_TO_LOADING"
    AT_LOADING_POSITION = "AT_LOADING_POSITION"
    EXTENDING_ARM = "EXTENDING_ARM"
    GRIPPING_BOX = "GRIPPING_BOX"
    PLACE_BOX = "PLACE_BOX"
    MOVING_TO_IDLE = "MOVING_TO_IDLE"


class RobotPosition(Enum):
    WAITING = "WAITING"
    LOADING = "LOADING"


class RobotController:
    def __init__(self) -> None:
        self.state = RobotState.IDLE
        self.position = None
        self.weight_sensor_kg = 0
        self.radar_clear = True  # Path is clear, gotten from sensors

        # Arm state
        self.arm_horizontal_m = 0
        self.arm_vertical_m = 0
        self.grip_active = False

        # Positiong to fetch from CB
        self.FETCH_X_m = 1.5
        self.FETCH_Y_m = 1.0

    def receive_message(self, msg_type, data=None):
        """Handle incoming messages from CB"""
        # robot_log(f"[ROBOT] Recieved: {msg_type} in state {self.state}")

        if msg_type == MessageType.LOADING_POSITION_VACANT:
            return self._handle_loading_position_vacant()
        elif msg_type == MessageType.FETCH_BOX:
            return self._handle_fetch_box()
        else:
            warning_log(f"[ROBOT] Warning: Unexpected message {msg_type}")
            return None

    def _handle_loading_position_vacant(self):
        """CB signals loading position is vacant"""
        # SAFETY CHECK: Only move if at waiting position
        if self.state != RobotState.AT_WAITING_POSITION:
            error_log(f"[ROBOT] ERROR: Cannot move to loading - not at waiting position!")
            return None

        # SAFETY CHECK: Radar must be clear
        if not self.radar_clear:
            error_log(f"[ROBOT] ERROR: Cannot move to loading - path not clear!")
            return None

        # Safe to proceed
        self.state = RobotState.MOVING_TO_LOADING
        return self._move_to_loading_position()  # FIXED: Return the message!

    def _handle_fetch_box(self):
        """CB signals box is ready to fetch"""
        # SAFETY CHECK: Must be at loading position
        if self.state != RobotState.AT_LOADING_POSITION:
            error_log(f"[ROBOT] ERROR: Cannot fetch - not at loading position!")
            return None

        # SAFETY CHECK: Arm must be retracted
        assert self.arm_horizontal_m == 0 and self.arm_vertical_m == 0

        # Safe to proceed - fetch the box
        self._fetch_box_sequence()

        # After fetching, send completion message
        return (MessageType.OPERATION_COMPLETE, None)

    def start_operation(self):
        """Initiates fetching operation (called by WMS/main)"""
        robot_log(f"[ROBOT] Starting operation")
        self.state = RobotState.MOVING_TO_WAITING
        return self._move_to_waiting_position()

    def _move_to_waiting_position(self):
        """Move to waiting position near CB"""
        robot_log(f"[ROBOT] Moving to waiting position...")
        sleep(1)  # Simulate movement (in real system: MoveToPosition(x, y))
        self.position = "WAITING"
        self.state = RobotState.AT_WAITING_POSITION
        robot_log(f"[ROBOT] Arrived at waiting position")

        return (MessageType.AT_WAITING_POSITION, None)

    def _move_to_loading_position(self):
        """Move from waiting to loading position"""
        robot_log(f"[ROBOT] Moving to loading position...")
        sleep(1)  # Simulate movement
        self.position = "LOADING"
        self.state = RobotState.AT_LOADING_POSITION
        robot_log(f"[ROBOT] Arrived at loading position")

        # Notify CB we're ready
        return (MessageType.READY_TO_RECEIVE, None)

    def _fetch_box_sequence(self):
        """Execute full box fetching sequence"""
        # Extend arm
        self.state = RobotState.EXTENDING_ARM
        robot_log(f"[ROBOT] Extending arm to ({self.FETCH_X_m}, {self.FETCH_Y_m})")
        sleep(1)  # Simulate arm movement
        self.arm_horizontal_m = self.FETCH_X_m
        self.arm_vertical_m = self.FETCH_Y_m

        # Grip box
        robot_log(f"[ROBOT] Gripping box")
        sleep(1)  # Simulate grip movement
        self.state = RobotState.GRIPPING_BOX
        self.grip_active = True

        # Place on platform (retract arm)
        robot_log(f"[ROBOT] Placing box on platform")
        sleep(1.5)  # Simulate retracting and placing
        self.state = RobotState.PLACE_BOX
        self.arm_horizontal_m = 0
        self.arm_vertical_m = 0
        self.grip_active = False

        # Simulate weight sensor detecting box
        self.weight_sensor_kg = 5.0  # kg
        robot_log(f"[ROBOT] Weight sensor: {self.weight_sensor_kg} kg detected")

        # SAFETY CHECK: Verify box was placed
        assert self.weight_sensor_kg > 0

        # Move away
        self.state = RobotState.MOVING_TO_IDLE
        robot_log(f"[ROBOT] Moving away from loading position")
        sleep(2)  # Simulate movement
        self.position = None

        # Return to idle
        self.state = RobotState.IDLE
        robot_log(f"[ROBOT] Operation complete, returning to IDLE")

    def get_state(self):
        """Return current state for monitoring"""
        return {
            "state": self.state,
            "position": self.position,
            "weight": self.weight_sensor_kg,
            "arm": (self.arm_horizontal_m, self.arm_vertical_m),
            "grip": self.grip_active,
        }

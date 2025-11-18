from enum import Enum
from time import sleep
from message import MessageType
from logger import cb_log, warning_log, error_log


class CBState(Enum):
    IDLE = "IDLE"
    LOADING_POSITION_VACANT = "LOADING_POSITION_VACANT"
    WAITING_FOR_ROBOT_READY = "WAITING_FOR_ROBOT_READY"
    TRANSPORTING_BOX = "TRANSPORTING_BOX"
    BOX_AT_FETCH_POSITION = "BOX_AT_FETCH_POSITION"


class CBController:
    def __init__(self) -> None:
        self.state = CBState.IDLE
        self.box_at_fetch_position = False
        self.loading_position_occupied = False
        self.belt_moving = False

        # Box position on belt (meters from start)
        self.box_position_m = 0
        self.FETCH_POSITION_m = 10.0  # Position where robot can fetch

    def receive_message(self, msg_type, data=None):
        """Handle incoming messages from Robot"""
        # cb_log(f"[CB] Received: {msg_type} in state {self.state}")

        if msg_type == MessageType.AT_WAITING_POSITION:
            return self._handle_at_waiting_position()
        elif msg_type == MessageType.READY_TO_RECEIVE:
            return self._handle_ready_to_receive()
        elif msg_type == MessageType.OPERATION_COMPLETE:
            return self._handle_operation_complete()
        else:
            warning_log(f"[CB] Warning: Unexpected message {msg_type}")
            return None

    def _handle_at_waiting_position(self):
        """Robot signals it's at waiting position"""
        # SAFETY CHECK: Must be in IDLE or ready state
        if self.state != CBState.IDLE:
            error_log(f"[CB] ERROR: Cannot signal vacant - not in IDLE state")
            return None

        # SAFETY CHECK: Loading position must not be occupied
        assert not self.loading_position_occupied

        cb_log(f"[CB] Robot at waiting position, signaling loading position vacant")
        self.state = CBState.LOADING_POSITION_VACANT

        return (MessageType.LOADING_POSITION_VACANT, None)

    def _handle_ready_to_receive(self):
        """Robot signals it's ready to receive box"""
        # SAFETY CHECK: Should be waiting for robot to arrive
        if self.state != CBState.LOADING_POSITION_VACANT:
            error_log(f"[CB] ERROR: Unexpected READY_TO_RECEIVE in state {self.state}")
            return None

        cb_log(f"[CB] Robot is ready, starting box transport")

        # Loading position now occupied
        self.loading_position_occupied = True
        self.state = CBState.WAITING_FOR_ROBOT_READY

        # Start async transport, then send FETCH_BOX
        self._transport_box()
        return (MessageType.FETCH_BOX, None)

    def _handle_operation_complete(self):
        """Robot signals operation is complete"""
        # SAFETY CHECK: Should be waiting for completion
        if self.state != CBState.BOX_AT_FETCH_POSITION:
            error_log(f"[CB] ERROR: Unexpected OPERATION_COMPLETE in state {self.state}")
            return None

        cb_log(f"[CB] Operation complete, returning to IDLE")

        # Reset state
        self.box_at_fetch_position = False
        self.loading_position_occupied = False
        self.box_position_m = 0
        self.state = CBState.IDLE

        return None

    def start_operation(self):
        """CB can be started (for testing), but typically waits for robot"""
        # In normal operation, CB just waits for AT_WAITING_POSITION
        # This method might not even be needed
        cb_log(f"[CB] Ready and waiting for robot")
        return None

    def _transport_box(self):
        """Transport box to fetch position"""
        self.state = CBState.TRANSPORTING_BOX
        cb_log(f"[CB] Transporting box to fetch position...")

        # Simulate belt movement
        self.belt_moving = True
        sleep(2)  # Simulate time to transport

        self.box_position_m = self.FETCH_POSITION_m
        self.belt_moving = False
        self.box_at_fetch_position = True

        cb_log(f"[CB] Box at fetch position, belt stopped")
        self.state = CBState.BOX_AT_FETCH_POSITION

        # SAFETY CHECK: Belt must be stopped before robot can fetch
        assert not self.belt_moving
        assert self.box_at_fetch_position

    def get_state(self):
        """Return current state for monitoring"""
        return {
            "state": self.state,
            "box_at_fetch": self.box_at_fetch_position,
            "loading_occupied": self.loading_position_occupied,
            "belt_moving": self.belt_moving,
            "box_position": self.box_position_m,
        }

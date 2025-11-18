from robot_controller import RobotController
from cb_controller import CBController
from logger import main_log


def main():
    """Main orchestrator - acts as message bus between controllers"""
    main_log("=" * 40)
    main_log("WAREHOUSE OPERATION SIMULATION")
    main_log("=" * 40)

    # Create controllers
    robot = RobotController()
    cb = CBController()

    # Message queue to pass between controllers
    message_queue = []

    main_log("\n[MAIN] Initializing operation...\n")

    # Start robot operation (WMS command)
    msg = robot.start_operation()
    if msg:
        message_queue.append(("CB", msg))

    # Process messages until queue is empty
    while message_queue:
        recipient, (msg_type, data) = message_queue.pop(0)

        main_log(f"\n[MAIN] Routing message {msg_type} to {recipient}")

        if recipient == "CB":
            # Send to CB
            response = cb.receive_message(msg_type, data)
            if response:
                message_queue.append(("ROBOT", response))

        elif recipient == "ROBOT":
            # Send to Robot
            response = robot.receive_message(msg_type, data)
            if response:
                message_queue.append(("CB", response))

        main_log(f"[MAIN] Message queue size: {len(message_queue)}")

    main_log("=" * 40)
    main_log("OPERATION COMPLETE")
    main_log("=" * 40)

    # Final states (for verification only)
    main_log(f"\nFinal Robot State: {robot.get_state()}")
    main_log(f"Final CB State: {cb.get_state()}")


if __name__ == "__main__":
    main()

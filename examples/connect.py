from jmaelossdk import AelosRobot


def main() -> None:
    robot = AelosRobot()
    robot.connect()
    print(f"Connected to {robot.port}")
    robot.close()


if __name__ == "__main__":
    main()

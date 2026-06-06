from jmaelossdk import AelosRobot


def main() -> None:
    ports = AelosRobot.list_ports()
    if not ports:
        print("No serial ports found.")
        return

    for port in ports:
        print(
            f"{port.device} score={port.score} "
            f"description={port.description!r} manufacturer={port.manufacturer!r}"
        )


if __name__ == "__main__":
    main()

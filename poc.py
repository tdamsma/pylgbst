from pylgbst.hub import MoveHub

hub = MoveHub()

for device in hub.peripherals:
    print(device)

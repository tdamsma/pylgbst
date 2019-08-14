import logging
import math
import sys
import time

from pylgbst.hub import MoveHub


def _clamp(minvalue, value, maxvalue):
    return max(minvalue, min(value, maxvalue))


class Joystick(object):
    def __init__(self):
        super(Joystick, self).__init__()
        self._on_joystick = set()
        self._hub = MoveHub()

        self._reset_sensors()

        self.button_pressed = False
        self._hub.button.subscribe(self._on_btn)

        self._angle_A = 0
        self._on_motor_a(self._on_a)

        self.angle_B = 0
        self.on_rotation(self._on_b)

        self._angle_C = 0
        self._on_motor_c(self._on_c)

        logging.info("Done initializing")

    def disconnect(self):
        self._hub.disconnect()

    def _reset_sensors(self):
        logging.info("Resetting motor encoders")
        self._hub.motor_A.preset_encoder()
        self._hub.motor_B.preset_encoder()
        self._hub.motor_external.preset_encoder()

    def on_button(self, callback):
        """
        Notifies about button state change. ``callback(state)`` gets single bool parameter
        """

        def wrapper(state):
            if state in (0, 1):
                callback(bool(state))

        self._hub.button.subscribe(wrapper)

    def _on_motor_a(self, callback):
        def wrapper(angle):
            logging.debug("Raw angle: %s", angle)
            spread = 25
            angle = _clamp(-spread, angle, spread)
            callback(angle)

        self._hub.motor_A.subscribe(wrapper)

    def on_rotation(self, callback):
        """
        Notifies about B motor rotation. ``callback(state)`` gets single int parameter from 0 to 359
        """

        def wrapper(angle):
            logging.debug("Raw angle: %s", angle)
            val = angle % 360
            callback(val if val >= 0 else 360 - val)

        self._hub.motor_B.subscribe(wrapper)

    def _on_motor_c(self, callback):
        def wrapper(angle):
            logging.debug("Raw angle: %s", angle)
            spread = 25
            angle = _clamp(-spread, angle, spread)
            callback(angle)

        self._hub.motor_external.subscribe(wrapper)

    def _on_btn(self, state):
        self.button_pressed = bool(state)

    def _on_a(self, angle):
        logging.debug("A rotated: %s", angle)
        self._angle_A = angle
        self._calc_joystick()

    def _on_b(self, angle):
        logging.debug("B rotated: %s", angle)
        self.angle_B = angle

    def _on_c(self, angle):
        logging.debug("C rotated: %s", angle)
        self._angle_C = angle
        self._calc_joystick()

    def on_joystick(self, callback):
        """
        Notifies about joystick change. ``callback(speed, direction)`` gets parameters:
        - ``speed`` - float value from 0.0 to 1.0
        - ``direction`` - int value from 0 to 359

        """
        self._on_joystick.add(callback)

    def _calc_joystick(self):
        norm_a = self._angle_A / 25
        norm_b = self._angle_C / 25
        logging.info("%s / %s", self._angle_A, self._angle_C)
        logging.info("%s / %s", norm_a, norm_b)
        speed = math.sqrt(norm_a ** 2 + norm_b ** 2) / math.sqrt(2)
        speed = _clamp(-1.0, speed, 1.0)

        maxsize = sys.maxsize if norm_a >= 0 else -sys.maxsize
        direction = math.atan(norm_a / norm_b if norm_b else maxsize)
        direction *= 180 / math.pi
        if norm_a >= 0 and norm_b >= 0:
            logging.info("Sector 1")
            direction = 90 - direction
        elif norm_a < 0 and norm_b >= 0:
            logging.info("Sector 2")
            direction = 90 - direction
        elif norm_a < 0 and norm_b < 0:
            logging.info("Sector 3")
            direction = 270 - direction
        else:
            logging.info("Sector 4")
            direction = 270 - direction

        for callback in self._on_joystick:
            callback(speed, 359 - int(direction))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    stick = Joystick()
    stick.on_button(lambda x: logging.info("Button: %s" % x))
    stick.on_rotation(lambda x: logging.info("Motor B: %s" % x))
    stick.on_joystick(lambda speed, head: logging.info("Speed: %.2f, dir: %s" % (speed, head)))
    time.sleep(100)

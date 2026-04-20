"""
Unit tests for all device classes in Tuya/devices/.
tinytuya.OutletDevice is mocked so no real network calls are made.
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, call

# Make sure the Tuya folder is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── shared DPS fixtures ───────────────────────────────────────────────────────

BREAKER_DPS = {
    '1': True, '17': 5000, '18': 1500, '19': 3300,
    '20': 2300, '26': 0, '38': 'power_on', '40': False,
}

HEATER_DPS = {
    '1': True, '9': 30, '38': 1, '40': False, '42': 2,
}

BULB_DPS = {
    '20': True, '21': 'white', '22': 500,
    '23': 300, '24': '000003e803e8', '25': '', '26': 0,
}

ESMAX_DPS = {
    '1': False, '2': 2, '3': True, '4': False,
    '5': 'zero', '101': 250, '102': 80, '103': 1200, '104': 50, '105': 0,
}

SMART_IR_DPS = {'1': None}

SMART_TV_DPS = {
    '1': True, '2': 50, '3': False, '4': 'standard', '102': 'HDMI1',
}

SMART_LOCK_DPS = {
    '1': None, '2': None, '3': None, '4': None,
    '21': 85, '38': None, '45': None, '50': None, '63': 'closed',
}

LOCK_DPS = {
    '1': None, '2': None, '3': None, '5': None, '7': None,
    '8': False, '9': None, '10': 75, '14': False, '61': False,
}

SMART_PLUG_DPS = {
    '1': True, '9': 0, '38': 'power_on', '40': False,
}

PRESENCE_DPS = {
    '1': True, '9': 150, '104': 320, '105': 'presence',
}

CONTACT_DPS = {
    '1': False, '2': 90, '3': 'high', '4': False,
}

GCB_DPS = {
    '1': True, '17': 0, '18': 0, '19': 0,
    '20': 0, '26': 0, '38': 'power_on', '40': False,
}

CONSUMPTION_DPS = {
    '1': True, '17': 8000, '18': 2000, '19': 4400,
    '20': 2300, '26': 0, '38': 'power_on', '40': False,
}


def make_mock_device(dps: dict) -> MagicMock:
    """Return a MagicMock that behaves like tinytuya.OutletDevice."""
    mock = MagicMock()
    mock.status.return_value = {'dps': dps}
    return mock


# ── breaker ───────────────────────────────────────────────────────────────────

class TestBreaker(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(BREAKER_DPS)):
            from devices.breaker import breaker
            self.cls = breaker
            self.dev = breaker('id1', '192.168.1.1', 'key1', 'Test Breaker')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id1')
        self.assertEqual(self.dev.ip, '192.168.1.1')
        self.assertEqual(self.dev.name, 'Test Breaker')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, BREAKER_DPS)

    def test_toggle_sends_opposite_state(self):
        result = self.dev.toggle()
        self.dev.device.set_dps.assert_called_with('1', False)  # was True
        self.assertFalse(result)

    def test_set_relay_status(self):
        self.dev.set_relay_status('power_off')
        self.dev.device.set_dps.assert_called_with('38', 'power_off')
        self.assertEqual(self.dev.relay_status, 'power_off')

    def test_set_childlock(self):
        self.dev.set_childlock()
        self.dev.device.set_dps.assert_called_with('40', True)


# ── consumption_breaker ───────────────────────────────────────────────────────

class TestConsumptionBreaker(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(CONSUMPTION_DPS)):
            from devices.consumption_breaker import consumption_breaker
            self.dev = consumption_breaker('id2', '192.168.1.2', 'key2', 'Consumption Breaker')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id2')
        self.assertEqual(self.dev.name, 'Consumption Breaker')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, CONSUMPTION_DPS)

    def test_toggle(self):
        self.dev.toggle()
        self.dev.device.set_dps.assert_called_with('1', False)  # was True

    def test_set_relay_status(self):
        self.dev.set_relay_status('last')
        self.dev.device.set_dps.assert_called_with('38', 'last')

    def test_set_childlock_toggles(self):
        self.dev.child_lock = False
        self.dev.set_childlock()
        self.dev.device.set_dps.assert_called_with('40', True)


# ── contact_sensor ────────────────────────────────────────────────────────────

class TestContactSensor(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(CONTACT_DPS)):
            from devices.contact_sensor import contact_sensor
            self.dev = contact_sensor('id3', '192.168.1.3', 'key3', 'Contact Sensor')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id3')
        self.assertEqual(self.dev.name, 'Contact Sensor')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, CONTACT_DPS)

    def test_door_closed(self):
        
        # dps '1' is False → door closed
        self.assertFalse(self.dev.dps.get('1'))

    def test_battery_percentage(self):
        self.assertEqual(self.dev.dps.get('2'), 90)

    def test_battery_state(self):
        self.assertEqual(self.dev.dps.get('3'), 'high')

    def test_tamper_alarm_off(self):
        self.assertFalse(self.dev.dps.get('4'))


# ── esmax ─────────────────────────────────────────────────────────────────────

class TestEsmax(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(ESMAX_DPS)):
            from devices.esmax import esmax
            self.dev = esmax('id4', '192.168.1.4', 'key4', 'ESMAX')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id4')
        self.assertEqual(self.dev.name, 'ESMAX')

    def test_initial_values(self):
        self.assertFalse(self.dev.switch_lock)
        self.assertEqual(self.dev.gear_set, 2)
        self.assertTrue(self.dev.light_switch)
        self.assertEqual(self.dev.speed, 250)
        self.assertEqual(self.dev.battery_level, 80)

    def test_set_gear_set(self):
        self.dev.set_gear_set(3)
        self.dev.device.set_dps.assert_called_with('2', 3)
        self.assertEqual(self.dev.gear_set, 3)

    def test_set_light_switch(self):
        self.dev.set_light_switch(False)
        self.dev.device.set_dps.assert_called_with('3', False)
        self.assertFalse(self.dev.light_switch)

    def test_set_cruise_control(self):
        self.dev.set_cruise_control(True)
        self.dev.device.set_dps.assert_called_with('4', True)
        self.assertTrue(self.dev.cruise_control)

    def test_set_start_mode(self):
        self.dev.set_start_mode('non_zero')
        self.dev.device.set_dps.assert_called_with('5', 'non_zero')
        self.assertEqual(self.dev.start_mode, 'non_zero')

    def test_toggle_switch_lock(self):
        self.dev.toogle_switch_lock()
        # switch_lock was False → should set True
        self.dev.device.set_dps.assert_called_with('1', True)


# ── general_circuit_breaker ───────────────────────────────────────────────────

class TestGeneralCircuitBreaker(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(GCB_DPS)):
            from devices.general_circuit_breaker import general_circuit_breaker
            self.dev = general_circuit_breaker('id5', '192.168.1.5', 'key5', 'GCB')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id5')
        self.assertEqual(self.dev.name, 'GCB')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, GCB_DPS)

    def test_toggle(self):
        self.dev.toggle()
        self.dev.device.set_dps.assert_called_with('1', False)  # was True

    def test_set_relay_status(self):
        self.dev.set_relay_status('power_off')
        self.dev.device.set_dps.assert_called_with('38', 'power_off')

    def test_set_childlock(self):
        self.dev.set_childlock()
        self.dev.device.set_dps.assert_called_with('40', True)


# ── heater ────────────────────────────────────────────────────────────────────

class TestHeater(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(HEATER_DPS)):
            from devices.heater import heater
            self.dev = heater('id6', '192.168.1.6', 'key6', 'Heater')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id6')
        self.assertEqual(self.dev.name, 'Heater')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, HEATER_DPS)

    def test_toggle(self):
        self.dev.toggle()
        self.dev.device.set_dps.assert_called_with('1', False)  # was True

    def test_set_countdown(self):
        self.dev.set_countdown(60)
        self.dev.device.set_dps.assert_called_with(60, '9')
        self.assertEqual(self.dev.countdown, 60)

    def test_set_relay_status(self):
        self.dev.set_relay_status(2)
        self.dev.device.set_dps.assert_called_with(2, '38')

    def test_set_child_lock(self):
        self.dev.set_child_lock(True)
        self.dev.device.set_dps.assert_called_with(True, '40')

    def test_set_switch_type(self):
        self.dev.set_switch_type(1)
        self.dev.device.set_dps.assert_called_with(1, '42')


# ── lock ──────────────────────────────────────────────────────────────────────

class TestLock(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(LOCK_DPS)):
            from devices.lock import lock
            self.dev = lock('id7', '192.168.1.7', 'key7', 'Lock')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id7')
        self.assertEqual(self.dev.name, 'Lock')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, LOCK_DPS)

    def test_door_closed(self):
        self.assertFalse(self.dev.dps.get('8'))

    def test_battery_level(self):
        self.assertEqual(self.dev.dps.get('10'), 75)

    def test_doorbell_not_pressed(self):
        self.assertFalse(self.dev.dps.get('14'))


# ── presence_sensor ───────────────────────────────────────────────────────────

class TestPresenceSensor(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(PRESENCE_DPS)):
            from devices.presence_sensor import presence_sensor
            self.dev = presence_sensor('id8', '192.168.1.8', 'key8', 'Presence Sensor')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id8')
        self.assertEqual(self.dev.name, 'Presence Sensor')

    def test_presence_detected(self):
        self.assertTrue(self.dev.dps.get('1'))

    def test_illuminance(self):
        self.assertEqual(self.dev.dps.get('104'), 320)

    def test_set_motion_state(self):
        self.dev.set_motion_state('large_move')
        self.dev.device.set_dps.assert_called_with('105', 'large_move')
        self.assertEqual(self.dev.motion_state, 'large_move')

    def test_toggle_indicator_switch(self):
        self.dev.toogle_indicator_switch()
        # dps '105' was 'presence' (truthy) → new state is False
        self.dev.device.set_dps.assert_called_with('105', False)


# ── smart_bulb ────────────────────────────────────────────────────────────────

class TestSmartBulb(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(BULB_DPS)):
            from devices.smart_bulb import smart_bulb
            self.dev = smart_bulb('id9', '192.168.1.9', 'key9', 'Smart Bulb')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id9')
        self.assertEqual(self.dev.name, 'Smart Bulb')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, BULB_DPS)

    def test_state_on(self):
        self.assertTrue(self.dev.dps.get('20'))

    def test_toggle(self):
        self.dev.Toogle()
        self.dev.device.set_dps.assert_called_with(False, '20')  # was True

    def test_set_brightness(self):
        self.dev.set_brightness(800)
        self.dev.device.dps_set.assert_called_with(800, '22')

    def test_set_colour(self):
        self.dev.set_colour('ff000003e803e8')
        self.dev.device.dps_set.assert_called_with('ff000003e803e8', '24')

    def test_set_mode(self):
        self.dev.set_mode('colour')
        self.dev.device.dps_set.assert_called_with('colour', '21')

    def test_set_temperature(self):
        self.dev.set_temperature(700)
        self.dev.device.dps_set.assert_called_with(700, '23')

    def test_set_scene(self):
        self.dev.set_scene('scene_data')
        self.dev.device.dps_set.assert_called_with('scene_data', '25')

    def test_set_countdown(self):
        self.dev.set_countdown(3600)
        self.dev.device.dps_set.assert_called_with(3600, '26')


# ── smart_ir ──────────────────────────────────────────────────────────────────

class TestSmartIR(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(SMART_IR_DPS)):
            from devices.smart_ir import smart_ir
            self.dev = smart_ir('id10', '192.168.1.10', 'key10', 'Smart IR')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id10')
        self.assertEqual(self.dev.name, 'Smart IR')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, SMART_IR_DPS)


# ── smart_lock ────────────────────────────────────────────────────────────────

class TestSmartLock(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(SMART_LOCK_DPS)):
            from devices.smart_lock import smart_lock
            self.dev = smart_lock('id11', '192.168.1.11', 'key11', 'Smart Lock')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id11')
        self.assertEqual(self.dev.name, 'Smart Lock')

    def test_dps_populated(self):
        self.assertEqual(self.dev.dps, SMART_LOCK_DPS)

    def test_door_state(self):
        self.assertEqual(self.dev.dps.get('63'), 'closed')


# ── smart_plug ────────────────────────────────────────────────────────────────

class TestSmartPlug(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(SMART_PLUG_DPS)):
            from devices.smart_plug import smart_plug
            self.dev = smart_plug('id12', '192.168.1.12', 'key12', 'Smart Plug')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id12')
        self.assertEqual(self.dev.name, 'Smart Plug')

    def test_state_on(self):
        self.assertTrue(self.dev.dps.get('1'))

    def test_toggle(self):
        self.dev.Toogle()
        self.dev.device.set_dps.assert_called_with('1', False)  # was True

    def test_set_countdown(self):
        self.dev.set_countdown(120)
        self.dev.device.set_dps.assert_called_with('9', 120)
        self.assertEqual(self.dev.countdown, 120)

    def test_set_relay_status(self):
        self.dev.set_relay_status('memory')
        self.dev.device.set_dps.assert_called_with('38', 'memory')

    def test_set_child_lock(self):
        self.dev.set_child_lock(True)
        self.dev.device.set_dps.assert_called_with('40', True)


# ── smart_tv ──────────────────────────────────────────────────────────────────

class TestSmartTV(unittest.TestCase):

    def setUp(self):
        with patch('tinytuya.OutletDevice', return_value=make_mock_device(SMART_TV_DPS)):
            from devices.smart_tv import smart_tv
            self.dev = smart_tv('id13', '192.168.1.13', 'key13', 'Smart TV')

    def test_init_stores_fields(self):
        self.assertEqual(self.dev.id, 'id13')
        self.assertEqual(self.dev.name, 'Smart TV')

    def test_power_on(self):
        self.assertTrue(self.dev.dps.get('1'))

    def test_toggle(self):
        self.dev.Toogle()
        self.dev.device.set_dps.assert_called_with('1', False)  # was True

    def test_set_volume(self):
        self.dev.set_volune(30)
        self.dev.device.dps_set.assert_called_with(30, '2')

    def test_set_mode(self):
        self.dev.set_mode('vivid')
        self.dev.device.dps_set.assert_called_with('vivid', '4')

    def test_set_source(self):
        self.dev.set_source('HDMI2')
        self.dev.device.dps_set.assert_called_with('HDMI2', '101')

    def test_set_tv_panel(self):
        self.dev.set_tv_pannel('ok')
        self.dev.device.dps_set.assert_called_with('ok', '16')

    def test_set_mute(self):
        self.dev.mute = False
        self.dev.set_mute()
        self.dev.device.set_dps.assert_called_with(True, '1')


# ── run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    unittest.main(verbosity=2)

import os

from dotenv import load_dotenv

from axis_camera_overlay import AxisCameraOverlayService

load_dotenv()

if __name__ == '__main__':
    test_loop2_packet = {
        'dateTime': 1769110006, 'usUnits': 1, 'trendIcon': 0, 'barometer': None, 'inTemp': 75.0, 'inHumidity': 27.0,
        'outTemp': 7.1, 'windSpeed': 11.0, 'windDir': 89.0, 'windSpeed10': 7.9, 'windSpeed2': 7.8, 'windGust10': 23.0,
        'windGustDir10': 67.0, 'dewpoint': -8.0, 'outHumidity': 51.0, 'heatindex': 7.0, 'windchill': -6.0, 'THSW': 1.0,
        'rainRate': 0.0, 'radiation': 244.0, 'stormRain': 0.0, 'dayRain': 0.0, 'rain15': 0.0, 'hourRain': 0.0,
        'dayET': 0.01, 'rain24': 0.0, 'bar_reduction': 2, 'bar_calibration': -0.001, 'pressure_raw': 13.785,
        'pressure': None, 'altimeter': 14.272, 'rain': 0.0, 'windGust': 12.0, 'windGustDir': 101.0,
        'appTemp': -5.659778478786329, 'cloudbase': 4074.7916950832, 'ET': None, 'humidex': 7.100000000000001,
        'inDewpoint': 38.73923583779798, 'maxSolarRad': 341.6190382377787, 'windrun': None
    }


    class MockEvent:
        packet = test_loop2_packet

    class MockEngine:
        def bind(self, event_type, callback):
            pass

    service = AxisCameraOverlayService(MockEngine(),
                                       {
                                           "AxisCameraOverlay": {
                                               "axis_host": os.getenv("AXIS_CAMERA_HOST"),
                                               "axis_user": os.getenv("AXIS_CAMERA_USER"),
                                               "axis_password": os.getenv("AXIS_CAMERA_PASSWORD")
                                           }
                                       })
    service.process_loop_packet(MockEvent())

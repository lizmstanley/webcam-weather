import logging

import requests
import weewx
from requests.auth import HTTPDigestAuth
from weewx.engine import StdService

log = logging.getLogger(__name__)

# See the README for instructions in integrating this with weewx
class AxisCameraOverlayService(StdService):

    def __init__(self, engine, config_dict):
        super(AxisCameraOverlayService, self).__init__(engine, config_dict)
        try:
            service_config = self.config_dict['AxisCameraOverlay']
            if not service_config:
                raise Exception('AxisCameraOverlay configuration not found')
            enabled = service_config.get('enabled', False)
            if not enabled:
                return
            # ip or host name of your axis camera
            axis_host = service_config.get('axis_host')
            if not axis_host:
                raise Exception('AxisCameraOverlay axis_host not set')
            self.axis_host = axis_host
            self.axis_overlay_url = f'http://{self.axis_host}/axis-cgi/dynamicoverlay.cgi'
            # create this user as an 'operator' under accounts in the camera system admin
            axis_user = service_config.get('axis_user')
            axis_password = service_config.get('axis_password')
            if not axis_user or not axis_password:
                raise Exception('AxisCameraOverlay camera credentials not set')
            self.auth = HTTPDigestAuth(axis_user, axis_password)
            self.bind(weewx.NEW_LOOP_PACKET, self.process_loop_packet)
            log.info('AxisCameraOverlayService initialized!')
        except Exception as e:
            log.error(f'Unable to initialize AxisCameraOverlayService due to: {e}')

    # Process incoming weather data (Davis LOOP2 packets) - make sure you updated weewx.conf for LOOP2 (see README)
    # Note that the dynamic text overlay API only supports GET calls.
    # This will update overlay text with the #D (dynamic) modifier, but leave other static text alone.
    def process_loop_packet(self, event):
        packet = event.packet
        # Set debug = 1 in weewx.conf to see debug output
        log.debug(f'Received packet {packet}')
        try:
            overlay_text_values = AxisCameraOverlayService.set_overlay_text_values(packet)
            params = {
                'action': 'settext',
                'text': AxisCameraOverlayService.build_overlay_text(overlay_text_values)
            }
            response = requests.get(self.axis_overlay_url, params=params, auth=self.auth, verify=False)
            log.debug(response.status_code)
            log.debug(response.url)
        except Exception as e:
            log.error(f'Unable to process packet due to {e}')

    # Extract data from the loop packet
    @staticmethod
    def set_overlay_text_values(packet):
        outdoor_temp = packet.get('outTemp')
        overlay_text_values = {
            'temperature': outdoor_temp,
            'dewpoint': packet.get('dewpoint'),
        }
        if packet.get('windGust') is not None and packet.get('windGustDir') is not None:
            overlay_text_values['wind_gust'] = packet.get('windGust')
            overlay_text_values['wind_dir'] = AxisCameraOverlayService.get_wind_cardinal_dir(packet.get('windGustDir'))
        elif packet.get('windSpeed') is not None and packet.get('windDir') is not None:
            overlay_text_values['wind_speed'] = packet.get('windSpeed')
            overlay_text_values['wind_dir'] = AxisCameraOverlayService.get_wind_cardinal_dir(packet.get('windDir'))
        if outdoor_temp > 60:
            overlay_text_values['humidity'] = packet.get('outHumidity')
        if 80 <= outdoor_temp < packet.get('heatindex'):
            overlay_text_values['heat_index'] = packet.get('heatindex')
        if 50 > outdoor_temp > packet.get('windchill'):
            overlay_text_values['wind_chill'] = packet.get('windchill')
        if packet.get('dayRain') > 0:
            overlay_text_values['rain'] = packet.get('dayRain')
        return overlay_text_values

    @staticmethod
    def build_overlay_text(overlay_text_values):
        text = f'Temp: {overlay_text_values['temperature']}°F | Dew: {overlay_text_values['dewpoint']}°F'
        if overlay_text_values.get('heat_index', None):
            text = f'{text} | Heat: {overlay_text_values['heat_index']}°F'
        if overlay_text_values.get('wind_chill', None):
            text = f'{text} | Chill: {overlay_text_values['wind_chill']}°F'
        if overlay_text_values.get('humidity') is not None:
            text = f'{text} | Humidity: {overlay_text_values['humidity']}%'
        if overlay_text_values.get('wind_gust') is not None and overlay_text_values.get(
                'wind_gust') > 0 and overlay_text_values.get('wind_dir') is not None:
            text = f'{text} | Wind Gust: {overlay_text_values['wind_gust']} {overlay_text_values['wind_dir']}'
        elif overlay_text_values.get('wind_speed') is not None and overlay_text_values.get(
                'wind_speed') > 0 and overlay_text_values.get('wind_dir') is not None:
            text = f'{text} | Wind: {overlay_text_values['wind_speed']} {overlay_text_values['wind_dir']}'
        else:
            text = f'{text} | Wind: calm'
        if overlay_text_values.get('rain', None):
            text = f'{text} | Rain: {overlay_text_values['rain']}in'
        log.debug(f'Built overlay text: {text}')
        return text

    @staticmethod
    def get_wind_cardinal_dir(wind_degrees_dir):
        if wind_degrees_dir is None:
            return None
        if wind_degrees_dir > 348.75: return 'N'
        if wind_degrees_dir > 226.25: return 'NNW'
        if wind_degrees_dir > 303.75: return 'NW'
        if wind_degrees_dir > 258.75: return 'W'
        if wind_degrees_dir > 236.25: return 'WSW'
        if wind_degrees_dir > 213.75: return 'SW'
        if wind_degrees_dir > 191.25: return 'SSW'
        if wind_degrees_dir > 168.75: return 'S'
        if wind_degrees_dir > 146.24:  return 'SSE'
        if wind_degrees_dir > 123.75: return 'SE'
        if wind_degrees_dir > 101.25: return 'ESE'
        if wind_degrees_dir > 78.75: return 'E'
        if wind_degrees_dir > 56.25: return 'ENE'
        if wind_degrees_dir > 33.75: return 'NE'
        if wind_degrees_dir > 11.25: return 'NNE'
        return 'N'

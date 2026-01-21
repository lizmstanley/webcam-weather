import logging
import requests
import weewx
from requests.auth import HTTPDigestAuth
from weewx.engine import StdService

log = logging.getLogger(__name__)

class AxisCameraOverlayService(StdService):

    def __init__(self, engine, config_dict):
        super(AxisCameraOverlayService, self).__init__(engine, config_dict)
        # ip of your axis camera
        self.axis_host= self.config_dict["AxisCameraOverlay"]["axis_host"]
        # create this user as an "operator" under accounts in the camera system admin
        self.auth = HTTPDigestAuth(self.config_dict["AxisCameraOverlay"]["axis_user"], self.config_dict["AxisCameraOverlay"]["axis_password"])
        self.bind(weewx.NEW_LOOP_PACKET, self.process_loop_packet)
        log.info("AxisCameraOverlayService initialized!")

    def process_loop_packet(self, event):
        # Process incoming weather data (LOOP packets)
        packet = event.packet
        log.debug(f"Received packet {packet}")
        outdoor_temp = packet.get("outTemp")
        overlay_text_values = {
            "temperature": outdoor_temp,
            "humidity": packet.get("outHumidity"),
            "dewpoint": packet.get("dewpoint"),
        }
        wind_speed = self.get_wind_speed(packet)
        wind_dir = self.get_wind_dir(packet)
        if wind_speed is not None and wind_dir is not None:
            overlay_text_values["wind_speed"] = wind_speed
            overlay_text_values["wind_dir"] = wind_dir
        if 80 <= outdoor_temp < packet.get("heatindex"):
            overlay_text_values["heat_index"] = packet.get("heatindex")
        if 50 > outdoor_temp > packet.get("windchill"):
            overlay_text_values["wind_chill"] = packet.get("windchill")
        if  packet.get("dayRain") > 0:
            overlay_text_values["rain"] =  packet.get("dayRain")
        params = {
            "action": "settext",
            "text": self.build_overlay_text(overlay_text_values)
        }
        axis_overlay_url = f"http://{self.axis_host}/axis-cgi/dynamicoverlay.cgi"
        response = requests.get(axis_overlay_url, params=params, auth=self.auth, verify=False)
        log.debug(response.status_code)
        log.debug(response.url)

    def get_wind_speed(self, packet):
        if packet.get("windSpeed") is not None:
            return packet.get("windSpeed")
        if packet.get("windSpeed2") is not None:
            return packet.get("windSpeed2")
        if packet.get("windSpeed10") is not None:
            return packet.get("windSpeed10")
        if packet.get("windGust") is not None:
            return packet.get("windGust")
        if packet.get("windGust10") is not None:
           return packet.get("windGust10")
        return None

    def get_wind_dir(self, packet):
        if packet.get("windDir") is not None:
            return self.wind_cardinal_dir(packet.get("windDir"))
        if packet.get("windGustDir") is not None:
            return self.wind_cardinal_dir(packet.get("windGustDir"))
        if packet.get("windGustDir10") is not None:
            return self.wind_cardinal_dir(packet.get("windGustDir10"))
        return None

    def build_overlay_text(self, overlay_text_values):
        text = f"Temp: {overlay_text_values['temperature']}°F | Humidity: {overlay_text_values['humidity']}% | Dew: {overlay_text_values['dewpoint']}°F"
        if overlay_text_values.get("wind_speed") is not None and overlay_text_values.get("wind_dir") is not None:
            text = f"{text} | Wind: {overlay_text_values['wind_speed']} {overlay_text_values['wind_dir']}"
        if overlay_text_values.get("heat_index", None):
            text = f"{text} | Heat: {overlay_text_values['heat_index']}°F"
        if overlay_text_values.get("wind_chill", None):
            text = f"{text} | Chill: {overlay_text_values['wind_chill']}°F"
        if overlay_text_values.get("rain", None):
            text = f"{text} | Rain: {overlay_text_values['rain']}in"
        return text

    def wind_cardinal_dir(self, wind_degrees_dir):
        if wind_degrees_dir is None:
            return None
        if wind_degrees_dir > 348.75: return "N"
        if wind_degrees_dir > 226.25: return "NNW"
        if wind_degrees_dir > 303.75: return "NW"
        if wind_degrees_dir > 258.75: return "W"
        if wind_degrees_dir > 236.25: return "WSW"
        if wind_degrees_dir > 213.75: return "SW"
        if wind_degrees_dir > 191.25: return "SSW"
        if wind_degrees_dir > 168.75: return "S"
        if wind_degrees_dir > 146.24:  return "SSE"
        if wind_degrees_dir > 123.75: return "SE"
        if wind_degrees_dir > 101.25: return "ESE"
        if wind_degrees_dir > 78.75: return "E"
        if wind_degrees_dir > 56.25: return "ENE"
        if wind_degrees_dir > 33.75: return "NE"
        if wind_degrees_dir > 11.25: return "NNE"
        return "N"
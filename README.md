## Webcam Weather Overlay for Davis Vantage Pro2 and Axis Network Cameras

I have run a [Davis Vantage Pro2](https://www.davisinstruments.com/products/wireless-vantage-pro2-with-24-hour-fan-aspirated-radiation-shield-and-weatherlink-console) personal 
weather station at my home since 2007, and have had a webcam on my bird feeders since 2008.

Because of Minnesota's harsh winters, I needed a camera that could withstand the cold temperatures without the need
for a dedicated heater. Most consumer grade electronics aren't rated for temperatures below freezing (32F), which can get down to
-20F or colder in the winter here.

The first iteration of Feedercam was a StarDot Netcam, which uploaded a still image every 30 seconds to my website.
The camera ran an embedded uCLinux OS, and allowed direct access via telnet. I was able to run shell scripts
and set up a cron job to pull data from an AmbientWeather WeatherHub2 IP server that I was using at the time to capture
weather data from the PWS.

Later, when YouTube streaming became available, I switched to an Axis P1365-E network camera to live stream my bird
feeders. Since Axis cameras only allow access via their API, I used a Zotax ZBOX mini PC running Linux to run shell scripts 
and pull the weather data from a Metobridge Pro running Meteohub. These scripts also ran as cron jobs, which called the Meteohub 
livedata CGI and then the Axis Dynamic Overlay API to overlay the weather data on the video stream. I installed the [CamStreamer app](https://camstreamer.com/camstreamer-about)
on the camera, which makes streaming to YouTube (and other platforms like Twitch, Windy, etc), very easy.

Currently I have an Axis P1375-E camera and connected an external microphone to it for audio. I continue to use the Davis 
Vantage Pro2, but I now have weewx running on a Beelink mini PC. Since weewx doesn't have a CGI or API to pull data, 
I decided to write a custom weewx service to process incoming loop packets, and call the Axis camera API to overlay the weather 
data on the stream. This is done in Python rather than shell scripts and doesn't require a cron job because it's running
within the weewx engine itself. Check out my [Feedercam](https://feedercam.overlookcircle.org) (shameless plug) see the result,
and maybe some cool birds too!

## Testing the service with your camera before deploying in weewx
You don't have to run this setup to use the service in weewx, but if you would like to run a test before deploying it in weewx, follow these steps:

1. `source ./setup.sh` in the root of the project.
1. `python weewx_axis/test_service.py`

## Setup your Axis Camera
1. Log into your Axis camera web interface.
1. Go to Settings -> System -> Accounts
1. Create a new account with "Operator" privileges, and set an account name and password. The account name will be the username.
1. Add static text on the image, including a placeholder for the dynamic text we'll be overlaying. For example: 
   1. Go to Video -> Overlays
   1. Add a Text overlay
   1. For mine I set this text to `Overlook Circle Feedercam | Bloomington MN | %D %T | #D`
   1. This will keep the static text on the image, with the placeholders for date (`%D`) and time (`%T`) being updated by the camera.
   1. The `#D` placeholder is for the dynamic overlay text, which will be updated by the weewx service.
1. Click "Modifiers" to see what other placeholders are available.
1. Set the font size, color, and position as desired.

### Setup in weewx
1. Copy the `weewx_axis/axis_weather_overlay.py` file to your weewx `/user` directory. Mine was in `/etc/weewx/bin/user`, but it may vary depending on your installation.
   1. If you have weewx running on another server, see the `scp_file.sh` script in this project. 
1. Edit your `weewx.conf` file to add the new service. Add the following (I put mine just before the `[Engine]` section):
      ```
      [AxisCameraOverlay]

       # The ip address of the axis camera
       axis_host = [your axis camera ip]

       # The user for accessing the camera dynamic overlay API.
       # Create this user with the "operator" role in the camera's system admin UI
       axis_user = [your axis user (the operator account name you created on the camera)]
       axis_password = [your axis password (for the operator account)]
      ```
1. In the `[Engine]` section of `weewx.conf`, in the `[[Services]]` sections, add the new service as `user.axis_camera_overlay.AxisCameraOverlayService`. 
   1. I added mine to the `restful_services` list. 
1. I'm using loop2 packets, which are supported by the Davis Vantage Pro2. These packets contain more accurate data with higher precision.
   1. This requires Davis firmware v1.90 or later.
   1. You'll need to update weewx.conf, which defaults to Loop1 packets. In the `[Vantage]` section, set `loop_request = 2`.
1. If you want to see debug output, change the `debug` level in the config file to `1`.
1. Restart weewx, for example `sudo systemctl restart weewx`.
1. Watch the logs to confirm the service initialized correctly, and to watch debug output, for example:
   1. `sudo tail -f /var/log/syslog | grep weewx`
   1. `sudo journalctl -u weewx -f`
      
Optionally edit the `axis_weather_overlay.py` file to customize the data fields that are displayed on the overlay, and/or 
if you prefer different weather values or want to change the logic I'm using there. 

Also if you have older Davis firmware that doesn't support loop 2 packets, you'll need to adjust the code accordingly for
loop 1 packet fields.

References:

* https://weewx.com/docs/5.2/hardware/vantage/#vantage_data - detail about Davis Vantage data fields.
* https://weewx.com/docs/5.2/custom/service-engine/#create-service - creating a custom weewx service.
* https://developer.axis.com/vapix/network-video/overlay-api/#dynamic-overlay-api - detail about the Axis Dynamic Overlay API.

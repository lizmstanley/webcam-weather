#!/usr/bin/env bash

# Edit your .env file to set WEEWX_USER, WEEWX_HOST, and WEEWX_USER_DIR before running this script.
# You'll need ssh running on the WEEWX host and have set up an ssh public private keypair for this to work.
source .env
scp ./weewx_axis/axis_camera_overlay.py ${WEEWX_USER}@${WEEWX_HOST}:${WEEWX_USER_DIR}/axis_camera_overlay.py
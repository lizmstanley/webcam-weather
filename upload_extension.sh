#!/usr/bin/env bash

# This script creates a tarball of the axis_camera_overlay extension and uploads it to the WEEWX host using ssh,
# to the directory specified by WEEWX_USER_DIR.
# It excludes test files and pycache directories from the tarball.

# Edit your .env file to set WEEWX_USER, WEEWX_HOST, and WEEWX_USER_DIR before running this script.
# You'll need ssh running on the WEEWX host and have set up an ssh public private keypair for this to work.
source .env
tar -czvf - --exclude='test*' --exclude='*pycache*' axis_camera_overlay | ssh ${WEEWX_USER}@${WEEWX_HOST} "cat > ${WEEWX_USER_DIR}/axis_camera_overlay.tgz"
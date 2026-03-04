from weecfg.extension import ExtensionInstaller

def loader():
    return AxisCameraOverlayServiceInstaller()

class AxisCameraOverlayServiceInstaller(ExtensionInstaller):
    def __init__(self):
        super(AxisCameraOverlayServiceInstaller, self).__init__(
            version='0.1',
            name='axis_overlay',
            description='Overlay Davis Vantage LOOP data on an Axis network camera video',
            author='Liz Stanley',
            author_email='lizmstanley@gmail.com',
            process_services='user.axis_camera_overlay.AxisCameraOverlayService',
            config={
                'AxisCameraOverlay': {
                    'enabled': True,
                    'axis_host': '[Axis camera host or ip]',
                    'axis_user': '[Axis camera operator user]',
                    'axis_password': '[Axis camera operator password]',
                },
            },
            files=[('bin/user', ['bin/user/axis_camera_overlay.py'])]
        )
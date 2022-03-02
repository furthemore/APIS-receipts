# APIS Receipts
This is the glue code that connects receipt printers, cash drawers, and barcode scanners to the APIS backend.
Supports decoding a US drivers license, validating a (SmartHealth Card)[https://smarthealth.cards/] QR code vaccination record, and opening QR code hyperlinks.


## Supported hardware
* ESC/POS network, USB, or serial printers.
* Serial, emulated serial, or IBM-HID (IBM SurePOS) mode barcode scanners

NB: Star printers are *NOT* supported - they do not directly understand ESC/POS, but there is a Windows middleware Star makes that might help.  We don't use Windows so I'm afraid you're on your own on that one.


## Technical overview

* Printing uses the [python-escpos library](https://pypi.org/project/python-escpos/)
  * Find documentation about configuring printer specifics with a YAML file [here](https://python-escpos.readthedocs.io/en/latest/user/usage.html?highlight=yaml#configuration-file).
* Communications with the backend takes place over an MQTT broker, [authenticated with a JWT](https://github.com/wiomoc/mosquitto-jwt-auth).

## Setup

1. Create a terminal configuration ("FireBases") in the APIS backend
2. Click "Provision app" and copy the credential under the QR code into settings.py
3. Set the `STATION_NAME` setting to match the MQTT username from the provisioning step.
4. If your MQTT broker uses a publically signed SSL certificate, set the SSL context to:
```
MQTT_TLS_CONTEXT = {
    "ca_certs": "/etc/ssl/certs/ca-certificates.crt"
}
```
4. Run either `mqtt_handler.py` (for printing) or `barcode_serial.py` (for barcode scanning) to test.
5. Run the install script to create a systemd unit that will keep these running in the background.

### Scanner Setup notes

1. Many Zebra scanners in "Serial Emulation" mode actually just enumerate as IBM-HID (aka IBM SurePOS or Fast-HID) under recent Linux kernels.   For these scanners, set the `USE_HID=1` environment variable (in `.env` for the systemd unit, or passed in).
2. You will probaly need udev rules that look like this (substitute vendor and product IDs to match your barcode scanner):
```
$ cat /etc/udev/rules.d/10-local.rules 
SUBSYSTEMS=="usb", ATTRS{idVendor}=="05e0", ATTRS{idProduct}=="0600", GROUP="plugdev", MODE="0777"
$ sudo udevadm control --reload-rules && sudo udevadm trigger
```

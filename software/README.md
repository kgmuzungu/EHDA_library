# EHDA - Electric Hidrodynamics Atomization library


# Main code Tutorial: (mainElectrospray.py)


In order to properly use the software the following steps should be followed:

### 1
Turn on all the devices (HS camera, FUG power supply, Wifi Oscilloscope, Back-light, Air flow and Syringe pump).

### 2
Turn on the computer, open the high speed camera software (PHOTRON). Click on update button on top-right in order to connect to the camera. Adjust the camera zoom and focus.

### 3
Open pycharm software with the code installed. (Or any IDE of preference).

### 4
Turn on the Wifi Oscilloscope and connect to it in the wifi of the computer. {(ATTENTION: Disconnect the oscilloscope Charger in order the avoid power line noise. Noise in oscilloscope measurement can block the classification to work.)}

### 5
Change the {save_path} attribute in file {/setup/nozzle/mapsetup.json} with the directory and filename where the program output should be saved.

### 6
Change the necessary attributes in file {/setup/nozzle/mapsetup.json} with the setup being used.

### 7
In case of running a control experiment. Change in file {/setup/nozzle/controlsetup.json} and in file {mainElectrospray.py} around line 32 change the variable {name_setup} to controlsetup.

### 8
Go to file {mainElectrospray.py}, click with right button and click the option {"run mainElectrospray.py"}
{(ATTENTION: The syringe pump must not be pumping when the software turns on, otherwise the commands sent to the syringe pump will be ignored by the pump.)}

### 9
Wait until the program finishes and the message "SAVE DATA THREAD FINISHED" to close it properly. In case of emergency the button "Q" can be pressed and hold for 5 seconds and the code will try to close all threads. The finishing process can take up to 1 minute to all be closed.


# Most Common Errors

### Failed connect to TiePie

    This error happens when the software could not connect to TiePie Wireless Oscilloscope.
    
    For that: 

## 1
 Check if the oscilloscope is connected to the wifi of the computer.
## 2
 Try to re-run the code.
    

### Failed connect to Fug - Power Supply

    This error happens when the software could not connect to fug High Voltage Power Supply.

    Normally this happens because the usb port that is connected on the computer is different than the one the software is trying to read.
    
    For that: 

## 1 
Try to run the code. Initially the code scan the ports available in the computer and shows which device is connected to each USB port.
## 2
Go to the file {mainElectrospray.py} around line 58 where is commented { PORTS} you should corretly input the port which is connected each device.


### Syringe Pump is not pumping in desired flow rates

    The software probably started with the pump in state {pumping}. In Order to work you can press the button "Start/Stop pump" in the syringe pump and the next command sent to the pump should work.





# USEFULL LINKS

https://medium.com/@gaelollivier/connect-to-your-raspberry-pi-from-anywhere-using-ngrok-801e9fd1dd46

https://www.influxdata.com

https://www.twilio.com/docs/iot/supersim/getting-started-super-sim-raspberry-pi-waveshare-4g-hat

https://docs.scipy.org/doc/scipy/reference/tutorial/fft.html

https://www.tiepie.com/en/libtiepie-sdk/linux#Downloads

http://api.tiepie.com/libtiepie/0.9.16/



# ACCOUNTS USED

Raspberry pi:
    user: lab
    pwd: 123lab

influx db:
	user: lab db
	pwd: 123lab123lab

grafana: 
	user: admin
	pwd: 123lab123lab


# WiFi IN THE RASPBERRY Pi: 

TiePie-WS6D-37426

TiePie-WS6D-37427


# wpa_supplicant.conf 
network={
        ssid="TiePie-WS6D-37427"
        key_mgmt=NONE
}


$ cd bin

$ ./pycharm.sh


# Always test the electrical conductivity (K [S/m]) of the liquid and update in the json file related.

* PUMP NE-100 commands: verify serial port to see the serial commands

https://smt.at/wp-content/uploads/smt-fug-Probus-V-Standard-IEEE-488-V15-englisch.pdf
https://pyexplabsys.readthedocs.io/drivers-autogen-only/fug.html


# VENV

python3 -m venv {nameOfEnvironment}
source /bin/activate


# git token for raspberry pi
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


# Python librarie for tiepie and FUG (not used yet)
pip install hvl-ccb


# influx db token:
30zF8j190P9AesW2fi60lkr_vkfG6vvUYg_OHtGqAJvywL92dTOxgS6y20F2LRvcn8DQZFgXDpgbY23W-44G-Q==


# Raspberry pi commands:

    # commands to mount usb driver


    # commands to connect to tiePie
    sudo systemctl start NetworkManager
    sudo systemctl status NetworkManager
    nmcli connection show
    nmcli device wifi connect <WIFI> password <PWD>
    nmcli d wifi list
    nmcli c down <WIFI>
    nmcli c up <WIFI> : to connect to a saved Wi-Fi network use

    # commands to evaluate threads
    ps -L -p <PID> -o pid,psr,command
    htop 
    lscpu     : list cpu
    ps -en -o pid,psr,command
    kill -9 pid

    # mount usb drive
    lsblk : list devices
    mount <from> <to>

    # change the boot file
    sudo nano /etc/rc.local

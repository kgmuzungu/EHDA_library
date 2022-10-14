

# electrospray library

#### liquid folder -> json files about the liquid
#### setup folder -> json files about the setup
#### json folder -> json files for tests purposes with data collected
#### literature folder -> files for diagrams purposes
#### offline treatment folder -> non real time process
#### serial_FUG folder -> power supply FUG control commands
#### serial_FUG folder -> pump control commands
#### viewer folder -> pump control commands
### viewer folder -> class that loads saved data in json and visualizes (plots) it, including FFT.
#### tiepie folder -> communication with oscilloscope control 


# To use this library you need to follow the steps bellow:


#### 1. Open the file: mainelectrospray_fug_allshapes.py

#### 2. Verify the file that is indicated in the variable "name_setup" in the url indicated in the variable "setup". 

    2.1. The "setup" indicates the url of where the file is located. 
    
    2.2. Open this file.

#### 3. Verify if the properties of the setup like "nozzle color", "camera to nozzle distance", "config", "nozzle to plate or ring distance", "nozzle diameter", "nozzle outside", "nozzle height", "high voltage", "diameter syringe", "units", "coflow gas type" is the same as yours in the 2.1.

    3.1. If not, create a json file in the "setup" folder with all the information and change the assignment string of the variable "name_setup" with the file created.

#### 4. Verify the file that is indicated in the variable "name_liquid" in the url indicated in the variable "liquid" url. 

    4.1. The "liquid" indicates the url of where the file is located. Open this file.
    4.2. You need to know which liquid you are dealing.

#### 5. If you would like to save all the information, the boolean assignment of the "VAR_BIN_CONFIG" should be = TRUE. If not, = FALSE.

#### 6. If you would like to have a voltage regime of RAMP, the boolean assignment of the "MODERAMP" should be = TRUE. 

    6.1. The RAMP mode is combined with the arbitrary assigment " number_measurements = 50 " because I saw that it is a good size for saving.
    6.2. The line from 221 until 226 indicates the information about txt_mode, slope, voltage_start, voltage_stop, step_size=0 and step_time=0. 
        6.2.1. Step_size and step_time = 0 because it is in the ramp mode. 
    6.3. Be sure that there is only one variable "number_measurments" assigment.
 
#### 7. If you would like to have a voltage regime of STEP, the boolean assignment of the "MODERAMP" should be = FALSE.

    7.1. The STEP mode is combined with the arbitrary assigment " number_measurements = 100 " because I saw that it is a good size for saving.
    7.2. The line from 208 until 213 indicates the information about txt_mode, slope, [](plot_generated)voltage_start, voltage_stop, step_size and step_time. Very intuitive what this means.

#### 8. To set the flow rate you can do in the software SyringePumpPro or manually in the pump.
    
    8.1. Verify if the flow rate (in the same file as 1) in the float variable assigment " Q = " is the one that you set. Make sure it is uL/h.
    8.2. Useful commands for pump, check the manual of the SeryngePumpPro : 
    
    *ADR0 
    RAT 5.0 [uL/h] 
    *BUZ5
    *VER \
    
    8.3. Do not format the PC or you will lose the license of this software.

#### 9. Verify if the path is the one that you would like to save in the variable "save_path".

#### 10. Run the file defined in 1.



# updates should be in in master branch 


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


Always test the electrical conductivity (K [S/m]) of the liquid and update in the json file related.

* PUMP NE-100 commands: verify serial port to see the serial commands

https://smt.at/wp-content/uploads/smt-fug-Probus-V-Standard-IEEE-488-V15-englisch.pdf
https://pyexplabsys.readthedocs.io/drivers-autogen-only/fug.html


# dry spray - ganan calvo

# ionizacao!
# E RUIDO!

# --- cortina de hidrogenio


# VENV


python3 -m venv {nameOfEnvironment}
source /bin/activate



# git token for raspberry pi
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

# Python librarie for tiepie and FUG 
pip install hvl-ccb

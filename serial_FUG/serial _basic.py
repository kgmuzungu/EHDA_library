""""

Release output
LED ON Send the command F1
With command F0 the unit can be switched off.

Set output voltage
Voltage setvalue TO 500V: U500

Set output current
Send the command: I70e-3 = 70mA
I70e-6
                                        ****************************
Choose the type of ramp function:
Send the command >S0B 2

Setting of resolution and measuring speed:
Send the command S7 (maximum with slowest measuring speed (long integration time))
The unit sends back answer string E0

Readback of actual voltage:
The actual voltage monitor is in register >M0
Query monitor register with command >M0?
In ideal case, the unit sends back the answer string M0:+5.00000E+02

Readback of actual current:
The actual current monitor is in register >M1
Query monitor register with command >M1?
                                        ****************************
Choose the type of ramp function:
Send the command >S0B 2

Setting of the ramp rate:
Send the command >S0R 25

Set the new setvalue:
Send the command U 1000

https://smt.at/wp-content/uploads/smt-fug-Probus-V-Standard-IEEE-488-V15-englisch.pdf

"""
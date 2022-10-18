from logic import *

dripping = Symbol("Dripping")
intermittent = Symbol("Intermittent")
conejet = Symbol("Conejet")
multijet = Symbol("Multijet")

modes = [dripping, intermittent, conejet, multijet]

shapes = ["Dripping", "Intermittent", "Conejet", "Multijet"]

symbols = []

# There must be a shape
knowledge = And(
    Or(dripping, intermittent, conejet, multijet),
)

for i in range(4):
    for shape in shapes:
        symbols.append(Symbol(f"{shape}{i}"))


# Each shape has a avg_number.
for shape in shapes:
    knowledge.add(Or(
        Symbol(f"{shape}0"),
        Symbol(f"{shape}1"),
        Symbol(f"{shape}1"),
        Symbol(f"{shape}3")
    ))

# Only one
# per shape.
for shape in shapes:
    for i in range(4):
        for j in range(4):
            if i != j:
                knowledge.add(Implication(
                    Symbol(f"{shape}{i}"), Not(Symbol(f"{shape}{j}"))
                ))


# Only one shape per number.
for i in range(4):
    for c1 in shapes:
        for c2 in shapes:
            if c1 != c2:
                knowledge.add(Implication(
                    Symbol(f"{c1}{i}"), Not(Symbol(f"{c2}{i}"))
                ))

def check_knowledge(knowledge):
    for symbol in shapes:
        if model_check(knowledge, symbol):
            print(f"{symbol}: YES", "green")
        elif not model_check(knowledge, Not(symbol)):
            print(f"{symbol}: MAYBE")


def check_classification(mean_value_var, std_dev_var,  med_var, psd_var, proportional_sum_var, sup_var, len_fourier_peaks_var):
    if mean_value_var < 0.5 or mean_value_var == 0.5:
        if (std_dev_var/mean_value_var) > 2.5:
            if (mean_value_var/med_var) < 0.9 or (mean_value_var/med_var) > 1.1:
                knowledge.add(dripping)
            if psd_var.any() < 0.2:
                knowledge.add(dripping)
                print("Dripping Sjaak")
                print("************")
    else:
        knowledge.add(Not(dripping))
        # mean_value - med < 1
        # mean_Value < 1

    if mean_value_var > 0.5 and mean_value_var > 0:
        if (std_dev_var / mean_value_var) > 2.5 and med_var > 0:
            if (mean_value_var / med_var) < 0.9 or (mean_value_var / med_var) > 1.1:
                knowledge.add(intermittent)
                print("Intermittent Sjaak")
                print("************")
            # ToDo: check this value different conditions
            if psd_var.any() > 0.2 and psd_var.any() < 0.75:
                print("Intermittent Sjaak")
                print("************")
            if len_fourier_peaks_var < 15:
                knowledge.add(intermittent)
                print("Intermittent Monica")
                print("************")
        else:
            knowledge.add(Not(intermittent))

    if mean_value_var > 1 and med_var > 0:
        if (mean_value_var / med_var) > 0.9 or (mean_value_var / med_var) < 1.1:
            if psd_var.any() > 0.0075: # 0.75
                print("Cone jet Sjaak")
                print("************")
                knowledge.add(conejet)
        # ToDo: check this value different conditions
            if psd_var.any() > 0.0009:
                print("Cone jet Monica")
                print("************")
            if med_var > 50:
                if len_fourier_peaks_var > 15:
                    print("Cone jet Monica")
                    print("************")
                    knowledge.add(conejet)
    else:
        knowledge.add(Not(conejet))

    if mean_value_var > 10:
        print("Multi-jet Sjaak")
        print("************")
        knowledge.add(multijet)
        if std_dev_var > 300:
            if sup_var > 1e3:
                if proportional_sum_var > 1e6:
                    if mean_value_var > 100:
                        print("Multi-jet Monica")
                        print("************")
                        knowledge.add(multijet)

    check_knowledge(knowledge)

"""

setup measurement
        resistance
            depending on ionization state few hundred MOhm to a few GOhm
            depending on how many charges are transported with the droplets
            in case of discharge, resistance goes down to zero
    initial plan with 100x amplification and 10kOhm shunt --> 1mV / nA
        high and low side (each) current limiting resistors
            10MOhm
                which would mean that if at 10kV the air gap resistance breaks down to 0Ohm a current of 10kV / 20MOhn = 5mA leading to a voltage drop over the shunt resistor, 10kOhm, of 50V
        current measurement shunt resistors    
            10kOhm
                @ 1nA --> 10uV
                @ 1uA --> 10mV
"""
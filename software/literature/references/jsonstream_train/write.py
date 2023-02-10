import jsonstreams
import os
import json


config_dict = {
    "nozzle color": "brown",
    "camera to nozzle distance": 16.5,
    "config": "nozzle to plate",
    "nozzle to plate or ring distance": 1.6,
    "nozzle diameter": 0.136,
    "nozzle outside": 0.091,
    "nozzle height": 3.5,
    "high voltage": "HV on the ground",
    "diameter syringe": "1.7",
    "units": "cm",
    "coflow gas type": "none",
    "osc_impedance": 2000000,
    "save_data": "True",
    "save_processing": "True",
    "save_config": "True",
    "save_json": "True",
    "save_path": "D:/Joao_Pedro/Joao_09-02-23",
    "number_camera_partitions": 10,
    "typeofmeasurement": {
        "sequence": "map",
        "voltage_start": 5000,
        "voltage_stop": 7000,
        "slope": 100000,
        "step_size": 500,
        "step_time": 2,
        "flow_rate": ["1.1", "1.2", "1.3", "1.4", "1.5"]
    }
}


sample_dict =  {
    "name": "setup/liquid/ethanol",
    "flow rate [m3/s]": "1.1",
    "voltage": "5001.71",
    "current PS": "3.06335e-08",
    "temperature": "0",
    "humidity": "0",
    "date and time": "Thu_09 Feb 2023",
    "target voltage": 5000,
    "mean": 56.754329681396484,
    "variance": 1492.234619140625,
    "deviation": 38.629451751708984,
    "median": 45.53459167480469,
    "rms": 68.65339660644531,
    "spray mode": [
        "Intermittent"
    ]
}



# Writing config
os.mkdir('experiment')
out_file = open("experiment/config.json", "w")
json.dump(config_dict, out_file, indent = 6)
out_file.close()


# Writing Data
with jsonstreams.Stream(jsonstreams.Type.OBJECT, filename='experiment/data.json', indent=4, pretty=True) as s:
    sample = 0
    while sample < 10:
        s.write('sample '+str(sample), sample_dict)
        sample +=1
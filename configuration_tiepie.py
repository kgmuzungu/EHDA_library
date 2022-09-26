import libtiepie

def config_TiePieScope(scp, sampling_frequency):
    # ToDo set input to single ended or differential
    # in oscilloscopechannel.py _get_is_differential or _get_impedance ... investigate further
    """print("SCP is differential: %s" % scp.channels[0].is_differential)
    print("SCP impedance: %s" % scp.channels[0].impedance)
    print("SCP is safe_ground: %s" % scp.channels[0].safe_ground_enabled)"""
    # !!!! input impedance by default is 2MOhm ... is in differential mode
    scp.measure_mode = libtiepie.MM_BLOCK
    scp.sample_frequency = sampling_frequency
    scp.record_length = 50000  # 10000 samples
    scp.pre_sample_ratio = 0  # 0 %
    scp.channels[0].enabled = True
    scp.channels[0].range = 4  # range in V
    # ToDo using autoranging would be an advantage?
    scp.channels[0].coupling = libtiepie.CK_DCV  # DC Volt
    scp.channels[0].trigger.enabled = True
    scp.channels[0].trigger.kind = libtiepie.TK_RISINGEDGE
    scp.channels[1].enabled = False
    scp.channels[2].enabled = False
    scp.channels[3].enabled = False
    scp.trigger_time_out = 100e-3  # 100 ms
    # Disable all channel trigger sources:
    for ch in scp.channels:
        ch.trigger.enabled = False
    # Setup channel trigger:
    ch = scp.channels[0]  # Ch 1
    # Enable trigger source:
    ch.trigger.enabled = True
    ch.trigger.kind = libtiepie.TK_RISINGEDGE  # Rising edge
    ch.trigger.levels[0] = 0.5  # 50 %
    ch.trigger.hystereses[0] = 0.05  # 5 %
    return scp

import serial

model = "FUG HPC"
pol_dict = {
    "+": 0,
    "-": 1
}
pol_inv = {v: k for k, v in pol_dict.items()}


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class CommunicationError(Error):
    def __init__(self, query, reply):
        self.query = query
        self.reply = reply

    def __str__(self):
        return f'Unexpected {model} reply "{self.reply}" to query "{self.query}"'


class FugHpcGeneric:
    def __init__(self, max_rcv_trials, verbose):
        self.max_rcv_trials = max_rcv_trials
        self.verbose = verbose

    # Needs to be implemented in derived class
    def _send_raw(self, query):
        pass

    # Needs to be implemented in derived class
    def _receive_raw(self):
        return None

    def send_cmd(self, cmd, check_reply="E0", silent=False):
        verbose = self.verbose - int(silent)
        if verbose > 0:
            print(f'{model} query: "{cmd}"')
        self._send_raw(cmd)
        trials = 0
        reply = ""
        while trials < self.max_rcv_trials:
            trials += 1
            reply = self._receive_raw()
            if reply:
                break
        if verbose > 0:
            print(f'{model} reply after {trials} trials: "{reply}"')
        if check_reply is not None:
            if reply == check_reply:
                return None
            else:
                raise CommunicationError(cmd, reply)
        return reply

    def get_register(self, register, silent=False):
        query = f">{register}?"
        reply = self.send_cmd(query, check_reply=None, silent=silent)
        if reply[:(len(register) + 1)] == f"{register}:":
            return reply[(len(register) + 1):]
        raise CommunicationError(query, reply)

    def set_register(self, register, value, silent=False):
        self.send_cmd(f">{register} {value}", silent=silent)
        return self.get_register(register, silent=silent)

    def reset(self):
        self.send_cmd("=")

    def set_u(self, u):
        return float(self.set_register("S0", u))

    def get_u(self, silent=False):
        return float(self.get_register("M0", silent=silent))

    def get_u_set(self, silent=False):
        return float(self.get_register("S0", silent=silent))

    def set_i(self, i):
        return float(self.set_register("S1", i))

    def get_i(self, silent=False):
        return float(self.get_register("M1", silent=silent))

    def get_i_set(self, silent=False):
        return float(self.get_register("S1", silent=silent))

    def set_ramp_speed(self, speed):
        return float(self.set_register("S0R", speed))

    def get_ramp_speed(self, silent=False):
        return float(self.get_register("S0R", silent=silent))

    def set_ramp_behaviour(self, behaviour):
        return int(self.set_register("S0B", behaviour))

    def get_ramp_behaviour(self, silent=False):
        return int(self.get_register("S0B", silent=silent))

    def set_output_state(self, state):
        return int(self.set_register("BON", state))

    def get_output_state(self, silent=False):
        return int(self.get_register("DON", silent=silent))

    def kill(self):
        return self.set_output_state(0)

    def set_polarity(self, pol):
        return pol_inv[int(self.set_register("BX", pol_dict[pol]))]

    def get_polarity(self, silent=False):
        return pol_inv[int(self.get_register("DX", silent=silent))]

    def get_polarity_set(self, silent=False):
        return pol_inv[int(self.get_register("BX", silent=silent))]


class FugHpcSerial(FugHpcGeneric):
    baud_rate = 115200

    def __init__(self, port, timeout_s=1, max_rcv_trials=3, verbose=0):
        super().__init__(max_rcv_trials, verbose)
        self.ser = serial.Serial(port, self.baud_rate, timeout=timeout_s)
        self.ser.reset_input_buffer()

    def __del__(self):
        self.ser.close()

    def _send_raw(self, query):
        self.ser.write(f"{query}\n".encode("ascii"))

    def _receive_raw(self):
        try:
            return self.ser.readline().decode("ascii")[:-1]
        except UnicodeError:
            return ""

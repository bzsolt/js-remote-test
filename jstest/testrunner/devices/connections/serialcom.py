# Copyright 2017-present Samsung Electronics Co., Ltd. and other contributors
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import serial

from jstest.common.utils import TimeoutException


class SerialConnection():
    '''
    The serial communication wrapper.
    '''
    def __init__(self, device_info):
        self.id = device_info['dev-id']
        self.baud = device_info['baud']
        self.timeout = device_info['timeout']

        # Defines the end of the stdout.
        self.prompt = device_info['prompt']

    def open(self):
        '''
        Open the serial port.
        '''
        self.serial = serial.Serial(port=self.id, baudrate=self.baud, timeout=self.timeout)

        # Press enters to start the serial communication.
        self.exec_command('\n\n')

    def close(self):
        '''
        Close the serial port.
        '''
        self.serial.close()

    def getc(self, size):
        '''
        Receive data from the serial port.
        '''
        time.sleep(2)

        return self.serial.read(size) or None

    def putc(self, data):
        '''
        Send data to the serial port.
        '''
        if isinstance(data, str):
            data = data.encode('utf8')

        return self.serial.write(data + '\n')

    def readline(self):
        '''
        Read line from the serial port.
        '''
        return self.serial.readline()

    def exec_command(self, cmd):
        '''
        Send command over the serial port.
        '''
        if isinstance(cmd, str):
            cmd = cmd.encode('utf8')

        self.serial.write(cmd + '\n')

        receive = self.serial.read_until(self.prompt)

        # Throw exception when timeout happens.
        if self.prompt not in receive:
            raise TimeoutException

        # Note: since the received data format is
        #
        #   [command][CRLF][stdout][CRFL][prompt],
        #
        # we should process the output for the stdout.
        return '\n'.join(receive.split('\r\n')[1:-1])

    def read_until(self, *args):
        '''
        Read data until it contains args.
        '''
        line = bytearray()
        while True:
            c = self.serial.read(1)
            if c:
                line += c
                for stdout in args:
                    if line[-len(stdout):] == stdout:
                        return stdout, bytes(line)
            else:
                raise TimeoutException

        return False, False

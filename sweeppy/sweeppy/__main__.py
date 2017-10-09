from __future__ import division
import itertools
import sys
from . import Sweep
import csv
from calendar import timegm
from datetime import datetime
import time
import socket

def main():
    if len(sys.argv) < 2:
        sys.exit('python -m sweeppy /dev/ttyUSB0')

    dev = sys.argv[1]
    t_end = time.time() + 60 * 10

    with Sweep(dev) as sweep:
        speed = sweep.get_motor_speed()
        rate = sweep.get_sample_rate()

        print('Motor Speed: {} Hz'.format(speed))
        print('Sample Rate: {} Hz'.format(rate))
        dated_filename = "{}__{:%Y-%m-%d_%H-%M-%S}.csv".format(socket.gethostname(), datetime.now())

        sweep.set_motor_speed(4)

        speed = sweep.get_motor_speed()
        print('Motor Speed: {} Hz'.format(speed))

        sweep.set_sample_rate(1000)
        rate = sweep.get_sample_rate()
        print('Sample Rate: {} Hz'.format(rate))

        # Starts scanning as soon as the motor is ready
        sweep.start_scanning()
        print('Started scanning.')

        with open(dated_filename, 'w') as open_writable_file:
            fieldnames = ['TIMESTAMP', 'AZIMUTH', 'DISTANCE', 'SIGNAL_STRENGTH']
            writer = csv.DictWriter(open_writable_file, fieldnames=fieldnames)
            writer.writeheader()

            # get_scans is coroutine-based generator lazily returning scans ad infinitum
            for scan in itertools.islice(sweep.get_scans(), 0, None):
                # print('Entering next scan')
                # print(scan)
                # print('{}\n'.format(scan))
                # print('Hi {}\n'.format(scan.samples))
                samples = scan.samples
                # print(type(samples[0]))
                # timestamp = timegm(datetime.utcnow().utctimetuple())
                timestamp = time.time()*1000

                for sample in samples:
                    writer.writerow({
                        'TIMESTAMP': timestamp,
                        'AZIMUTH': sample.angle / 1000,
                        'DISTANCE': sample.distance,
                        'SIGNAL_STRENGTH': sample.signal_strength
                    })
                    # print('Angle: {}'.format(sample.angle))
                    # print('Distance: {}'.format(sample.distance))
                    # print('Strength: {}'.format(sample.signal_strength))
                    timestamp = -1
                if time.time() >= t_end:
                    break

        print('Stopping Scan.')
        sweep.stop_scanning()
        print('Scan Stopped.')
        print('Motor Speed: {} Hz. Turning motor speed to 0 Hz...'.format(speed))
        sweep.set_motor_speed(0)
        print('Motor speed set to 0 Hz. Hopefully it is stopped.')
main()
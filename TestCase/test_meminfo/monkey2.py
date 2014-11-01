import os

import monkey

def main():
    packages = os.popen('adb shell pm list package -s').readlines()
    for package in packages:
        package = package[8:].strip()
        lines = os.popen('adb shell monkey -p {0} -v 0'.format(package)).readlines()
        if len(lines) > 5:
            command = 'monkey -p {0} -s 10 --throttle 500 --ignore-timeouts --ignore-crashes -v 20000'.format(package)
            monkey.dumpsys_meminfo(command, 180, 'monkey-{0}'.format(package))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
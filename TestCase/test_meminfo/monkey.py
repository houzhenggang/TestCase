import os
import subprocess
import sys
import threading
import time

class DumpsysMeminfoThread(threading.Thread):

    def __init__(self, interval, output):
        threading.Thread.__init__(self)
        self.interval = interval
        self.output = output
        self.loop = True

    def run(self):
        while self.loop:
            time.sleep(self.interval)
            subprocess.Popen('adb shell dumpsys meminfo', shell=True, stdout=self.output, stderr=self.output).wait()

    def stop(self):
        self.loop = False

def report(meminfo, output):
    list = []
    data = {}
    enter = False
    for line in meminfo.readlines():
        if line.startswith('Total PSS by process:'):
            enter = True
        elif line.startswith('Total PSS by OOM adjustment:'):
            enter = False
        elif enter and line.strip():
            array = line.strip().split(' ')
            data[array[2]] = array[0]
        elif line.startswith('Total RAM:'):
            data['Total RAM'] = line.strip().split(' ')[2]
        elif line.startswith(' Free RAM:'):
            data['Free RAM'] = line.strip().split(' ')[2]
        elif line.startswith(' Used RAM:'):
            data['Used RAM'] = line.strip().split(' ')[2]
        elif line.startswith(' Lost RAM:'):
            data['Lost RAM'] = line.strip().split(' ')[2]
            list.append(data.copy())
            data.clear()
        elif line.startswith('Total PSS:'):
            list.append(data.copy())
            data.clear()

    if len(list) > 0:
        # write to file
        title = max(list).keys()
        title = [t for t in title if t not in ['Total RAM', 'Free RAM', 'Used RAM', 'Lost RAM']]
        title[0:0] = ['Total RAM', 'Free RAM', 'Used RAM', 'Lost RAM']
        output.write(','.join(title) + '\n')
        for item in list:
            for i in range(len(title)):
                if i == 0:
                    output.write(item.get(title[i], '0'))
                else:
                    output.write(',' + item.get(title[i], '0'))
            output.write('\n')

def dumpsys_meminfo(command, interval, outdir):
    model = os.popen('adb shell getprop ro.product.model').readline().strip()
    workdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    monkey_model = os.path.join(workdir, model)
    if not os.path.exists(monkey_model):
        os.mkdir(monkey_model)
    monkey_outdir = os.path.join(monkey_model, outdir)
    if not os.path.exists(monkey_outdir):
        os.mkdir(monkey_outdir)

    # before monkey
    meminf_before = open(os.path.join(monkey_outdir, 'before.txt'), 'w+')
    subprocess.Popen('adb shell dumpsys meminfo', shell=True, stdout=meminf_before, stderr=meminf_before).wait()
    meminf_before.flush()
    meminf_before.seek(0)
    report_before = open(os.path.join(monkey_outdir, 'before.csv'), 'w')
    report(meminf_before, report_before)
    report_before.close()
    meminf_before.close()

    # process monkey
    meminf_process = open(os.path.join(monkey_outdir, 'process.txt'), 'w+')
    t = DumpsysMeminfoThread(interval, meminf_process)
    t.start()
    os.system('adb shell {0}'.format(command))
    t.stop()
    t.join()
    meminf_process.flush()
    meminf_process.seek(0)
    report_process = open(os.path.join(monkey_outdir, 'process.csv'), 'w')
    report(meminf_process, report_process)
    report_process.close()
    meminf_process.close()

    # after monkey
    meminf_after = open(os.path.join(monkey_outdir, 'after.txt'), 'w+')
    subprocess.Popen('adb shell dumpsys meminfo', shell=True, stdout=meminf_after, stderr=meminf_after).wait()
    meminf_after.flush()
    meminf_after.seek(0)
    report_after = open(os.path.join(monkey_outdir, 'after.csv'), 'w')
    report(meminf_after, report_after)
    report_after.close()
    meminf_after.close()

def main():
    dumpsys_meminfo('monkey -s 10 --throttle 500 --ignore-timeouts --ignore-crashes -v 200000', 1800, 'monkey')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

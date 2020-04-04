# -*-coding:utf-8-*-
import frida
import sys
import time
import logging
import analysis
import subprocess
import os, threading

path = "/Users/maomao/Desktop/malware_log.txt"

class Monitor(object):
    device = None
    apkFile = None
    pid = None
    attached = False
    serial = "8XV7N16401000213"
    api_state = list()

    def __init__(self, apkFile):
        self.apkFile = apkFile
        self.setLogPath(path)
        self.logger = logging.getLogger("Moinitor")
        self._observers = []
        self.packageName = None
        self.session = None

    #设置monitor各参数，启动monitor监听app
    def set_up(self):
        self.setLogPath(path)
        # self.addObserver(pidObserver())
        # self.addObserver(attachObserver())
        self.wait_for_devices()
        self.start_server()
        packageName = self.start_app()
        self.attach(packageName)
        self.load_script(self.session, self.pid)
        return

    def setLogPath(self, log_path):
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(message)s",
                            datefmt='%Y-%m-%d %H:%M',
                            filename=path,
                            filemode="w")

    def build_monitor_script(self, dir, topdown=True):
        script = ""
        for root, dirs, files in os.walk(dir, topdown):
            for name in files:
                script += open(os.path.join(root, name)).read()
        return script

    def on_message(self, message, data):
        if message['type'] == 'send':
            logging.info(message['payload'])
            msg = message['payload']
            self.api_state.append(msg)
        elif message['type'] == 'error':
            logging.info(message['stack'])

    #启动app
    def startApp(self,apkFile, packageName, launcherActivity):
        # install apk
        if self.apkFile != None:
            cmd = "adb install -r " + self.apkFile
            ret = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if (ret == 1):
                print("[ERROR]: failed install apk")
                self.notify()
                sys.exit(-1)
            else:
                print("successfully installed apk")


            # launch app
            cmd = "adb shell am start -n " + packageName + "/" + launcherActivity
            ret = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if (ret == 1):
                print("[ERROR]: failed to launch app")
                sys.exit(1)
            print("successfully launched app")

            # prepare for frida
            cmd = "adb forward tcp:27042 tcp:27042"
            ret = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #启动测试机中的frida-server
    def start_server(self):
        task = threading.Thread(target=self.startServer)
        task.start()

    def startServer(self):
        cmd = "./start.sh"
        ret = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if (ret == 1):
            print("frida-server start failed !!!")
            sys.exit(1)

    def start_app(self):
        apkFile = self.apkFile
        app = analysis.Application(apkFile)
        self.packageName = app.getPackageName()
        launcherActivity = app.getMainActivity()
        # install apk and launch app
        self.startApp(apkFile, self.packageName, launcherActivity)
        print("app start")
        # wait for app
        time.sleep(10)
        return self.packageName

    def attach(self, packageName):
        try:
            self.device = frida.get_usb_device()
            self.pid = self.device.spawn([packageName])
            self.session = self.device.attach(self.pid)
        except Exception as e:
            print("[ERROR]: %s" % str(e))
            print("waiting for process")
            #self.notify()
            return None
        self.attached = True
        print("successfully attached to app")

    def detach(self, session):
        session.detach()
        self.attached = False

    def load_script(self, session, pid):
        if self.attached:
            script_dir = os.path.join(".", "scripts")
            script_content = self.build_monitor_script(script_dir)
            script = session.create_script(script_content)
            script.on("message", self.on_message)
            script.load()
            self.device.resume(pid)

    def addObserver(self, observer):
        self._observers.append(observer)

    def getPid(self):
        cmd = "adb shell ps | grep " + self.packageName
        result = os.popen(cmd)
        if result is not None:
            return self.pid
        else:
            cmd = "frida-ps -U"
            temp_pid = None
            result = os.popen(cmd)
            for i in result.readlines():
                if self.packageName != None and self.packageName in i:
                    temp_pid = i.split("  ")[0]
                    break
                else:
                    temp_pid = None
                    print("Process not found")
            self.pid = temp_pid
        #self.notify()
        return self.pid

    def getDevice(self):
        try:
            out = subprocess.check_output(["adb", "-s", self.serial, "shell",
                                           "getprop", "init.svc.bootanim"]).split()[0]

        except Exception as e:
            print("Device not found")
            self.device = None
        return
    def check_env(self):
        self.getPid()
        self.getDevice()
        if not self.device:
            self.wait_for_devices()
            self.set_up()
            return
        if not self.pid:
            if self.attached is True:
                self.detach(self.session)
        else:
            if self.attached == False:
                self.attach(self.packageName)
                self.load_script(self.session, self.pid)
            return

    # def getAttach(self):
    #     if(frida.get_usb_device == None):
    #         self.detach(self.session)
    #         self.attached = False
    #     self.notify()
    #     return self.attached

    def notify(self):
        for o in self._observers:
            o.update(self)

    def wait_for_devices(self):
        self.logger.info("waiting for device")
        try:
            #subprocess.check_call(["adb", "-s", self.serial, "wait-for-device"])
            while True:
                out = subprocess.check_output(["adb", "-s", self.serial, "shell",
                                               "getprop", "init.svc.bootanim"]).split()[0]
                if str(out) == "b\'stopped\'":
                    break
                time.sleep(3)
        except:
            self.logger.warning("error waiting for device")

    def get_api_state(self):
        temp_state = self.api_state
        self.api_state = list()
        return temp_state

    def stop(self):
        self.detach(self.session)
        print("stop monitor...")
        return

class Observer(object):
    def update(self, monitor):
        pass

class pidObserver(Observer):
    def update(self, monitor):
        if(monitor.pid == None):
            print("Not found pid")
            monitor.attach(monitor.packageName)

class attachObserver(Observer):
    def update(self, monitor):
        if(monitor.attached is False):
            print("Not found device")
            monitor.start_server()



def main():
    if len(sys.argv) != 2:
        print("usage: monitor.py example.apk")
        sys.exit(1)

    #get static info
    apkFile = sys.argv[1]

    #设置初始环境，启动monitor
    #apkFile = "/Users/maomao/Desktop/ADM_malware/FakeInst/variety2/0a7a631b5ad0c7c8013adba356597264.apk"
    m = Monitor(apkFile)
    m.set_up()

    #添加自动化测试，设置测试参数
    event_num = 10
    test_num = 10
    log_path = "/Users/maomao/Desktop/log/"
    log_name = "monkeytestlog.txt"
    monkey_shell = 'adb shell monkey -v -v -v -p ' + "com.soft.android.appinstaller" + ' -v ' + str(event_num) + ' >' + log_path

    for i in range(1, test_num + 1):
        print('The ', i, ' monkey test starting...')
        m.check_env()
        os.system(monkey_shell + str(i) + log_name)
        time.sleep(10)
        print(m.get_api_state())
        print(i, ' test complete!')
    print("monkey test complete")
    m.stop()
    sys.exit()


if __name__ == "__main__":
    main()






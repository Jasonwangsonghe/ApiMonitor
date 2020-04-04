from uiautomator import Device
import os, datetime

class automator:
    devicesName = ''
    savePath = '../tmp/'

    def __init__(self, deviceName):
        self.devicesName = deviceName
        print 'deviceName:', deviceName

    def execCmd(cmd):
        try :
            return os.popen(cmd).read()
        except Exception:
            return None

    def getChatInfoList(self, oneDevice):
        #dom = xml.dom.minidom.parse("../scripts/chaty.xml")
        #root = dom.documentElement
        #actionList = root.getElementsByTagName('action')
        #for actionElement in actionList:
        #    self.actionManage(actionElement, oneDevice
        #    self.resolveChatListByAttr('abc')
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print self.deviceName, '--', '**** begin to dump!!! *****', nowTime
        oneDevice.dump(self.savePath + 'chatInfoList.xml')
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print self.deviceName, '--', '**** finished to dump!!! *****', nowTime
        #self.resolveChatListByAttr(oneDevice)

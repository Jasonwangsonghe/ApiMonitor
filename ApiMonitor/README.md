## ApiMonitor

基于frida框架的Android动态检测工具，动态监控app运行时的敏感api调用行为



## Usage

### Windows/Linux/MacOS

1. 根据设备选择相应frida-server并安装(或直接安装frida1268_64)

```
adb push frida-server /data/local
```

2. 自行修改frida-server启动脚本

```
adb forward tcp:27042 tcp:27042
adb forward tcp:27043 tcp:27043

   expect -c"
   spawn adb shell
   expect \"shell@*\"
   send \"su\r\"
   expect \"root@*\"
   send \"./data/local/frida1268_64\r\"
   interact
"
```

3. 启动Monitor

```
python monitor.py target.apk
```







### 输出样例

```
The  2  monkey test starting...
['call libc->open', 'call libc->open', 'call libc->open', 'call libc->open']
2  test complete!
The  3  monkey test starting...
['call libc->open', 'call libc->open']
3  test complete!
The  4  monkey test starting...
[]
4  test complete!
```



### 日志信息

```
2020-03-15 12:20 call java.security.MessageDigest->getInstance for MD5
2020-03-15 12:20 call java.security.MessageDigest->getInstance for MD5
2020-03-15 12:20 call libc->open
2020-03-15 12:20 call libc->open
2020-03-15 12:20 call android.net.Uri->parse content://com.google.android.gms.chimera/api_force_staging/com.google.android.gms.ads.dynamite
2020-03-15 12:20 call android.content.ContentResolver->query
2020-03-15 12:20 call android.net.Uri->parse content://com.google.android.gms.chimera/api/com.google.android.gms.ads.dynamite
2020-03-15 12:20 call android.content.ContentResolver->query
2020-03-15 12:20 call android.net.Uri->parse content://com.google.android.gms.chimera/api/1582107570000
```




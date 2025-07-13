# mcw-crumbs-data
这一系列程序用于自动获取与处理Minecraft Wiki的一些数据。

## 功能列表
当前支持的功能包括：

### 编辑总数分布情况（`difftime.py`）
通过设置固定间隔获取多个做出修订的时间戳实现。

使用前，请自行根据需求修改`config.json`中的`num_diff`、`minrev`和`maxrev`字段，其中`minrev`和`maxrev`指定了搜索的范围，可以为空。

### 指定用户的所有贡献（`usercontribs.py`）
直接通过API获取。这些信息是其他程序的基础，因此存储为json文件。

使用前，请自行根据需求修改`config.json`中的`username`、`starttime`和`endtime`字段，其中`starttime`和`endtime`指定了搜索的时间范围，可以为空。`username`中的空格可以被下划线取代，而`starttime`和`endtime`必须遵守`<年>-<月>-<日>T<时>:<分>:<秒>Z`的格式，其中年份必须为4位数字，其他必须为2位数字。

### 指定用户的编辑时段（`editperiod.py`）
读取`usercontribs.py`产生的json文件，统计指定用户在一天24小时或一周7天，每小时或每天的编辑总数，并存储到两个工作表中。

使用前，请自行根据需求修改`config.json`中的`datafile`字段，其指定了`usercontribs.py`产生的json文件的名称，不需要带上后缀名。

### 过去一个月的活跃用户列表（`activeusers.py`）
获取过去一个月的所有最近更改情况，统计有哪些用户做出了多少次操作。用于取代存在漏洞的[[Special:活跃用户]]特殊页面。

根据实际需求，程序有特殊处理：
* 不统计创建账号操作
* 不统计IP用户的所有操作
* 不统计 _~~（用户名已移除）~~_ 的操作
* 本地用户组一栏，只注明本地用户组
* 程序会读取当前月份，然后进行如下操作（均指本地时间）：
1. 如果当前是2月，那么统计1月28日0时到2月25日0时的数据；
2. 如果当前是3月，那么统计2月25日0时到3月28日0时的数据；
3. 如果不符合上述情况，那么统计上月28日0时到本月28日0时的数据。

使用前，请自行根据需求修改`config.json`中的`usergroup_order`和`usergroup_mapping`字段。对中文Minecraft Wiki，这两个字段无需修改即可应用。`mode`字段默认为“standard”，若设置为“debug”，则从当前时刻减去当前秒数的时刻开始（如：现在是2025年8月19日05:35:xx，那么程序总是从2025年8月19日05:35:00开始），统计过去30天的数据，方便与[[Special:活跃用户]]特殊页面进行比较。

## 使用方法
程序需要同目录存在`config.json`才能正常运作。使用前，请自行修改`config.json`中的用户代理。如果不设置用户代理，任何请求都会被服务器拒绝。

程序支持不同语言的Minecraft Wiki，可以通过修改`config.json`的`wiki`字段切换。当前支持的语言包括：
* `de`
* `en`
* `es`
* `fr`
* `it`
* `ja`
* `ko`
* `lzh`
* `nl`
* `pt`
* `ru`
* `th`
* `uk`
* `zh`
* `meta`

程序支持不同时区，可以通过修改`config.json`的`timezone`字段切换。

## 授权协议
程序采用与Minecraft Wiki相同的CC BY-NC-SA 3.0协议授权。

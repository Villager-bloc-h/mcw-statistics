# mcw-crumbs-data
这一系列程序用于自动获取Minecraft Wiki的一些数据。

## 功能列表
当前支持获取的数据包括：

### 编辑总数分布情况（`difftime.py`）
通过设置固定间隔获取多个做出修订的时间戳实现。

使用前，请自行根据需求修改`config.json`中的`num_diff`、`minrev`和`maxrev`字段，其中`minrev`和`maxrev`指定了搜索的范围，可以为空。

### 指定用户的所有贡献（`usercontribs.py`）
直接通过API获取。这些信息是其他程序的基础，因此存储为json文件。

使用前，请自行根据需求修改`config.json`中的`username`、`starttime`和`endtime`字段，其中`starttime`和`endtime`指定了搜索的时间范围，可以为空。`username`中的空格可以被下划线取代，而`starttime`和`endtime`必须遵守`<年>-<月>-<日>T<时>:<分>:<秒>Z`的格式，其中年份必须为4位数字，其他必须为2位数字。

### 指定用户的编辑时段（`editperiod.py`）
读取`usercontribs.py`产生的json文件，统计指定用户在一天24小时或一周7天，每小时或每天的编辑总数，并存储到两个工作表中。

使用前，请自行根据需求修改`config.json`中的`datafile`字段，其指定了`usercontribs.py`产生的json文件的名称，不需要带上后缀名。

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

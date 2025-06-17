# mcw-crumbs-data
这一系列程序用于自动获取Minecraft Wiki的一些数据。

## 功能列表
当前支持获取的数据包括：

### 编辑总数分布情况
通过设置固定间隔获取多个做出修订的时间戳实现。

使用前，请自行根据需求修改`config.json`中的`num_diff`、`minrev`和`maxrev`字段，其中`minrev`和`maxrev`指定了搜索的范围，可以为空。

## 使用方法
程序需要同目录存在`config.json`才能正常运作。使用前，请自行修改`config.json`中的用户代理。

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

## 授权协议
程序采用与Minecraft Wiki相同的CC BY-NC-SA 3.0协议授权。

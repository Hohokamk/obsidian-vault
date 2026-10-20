  

URL 是什么

**URL** 是 **Uniform Resource Locator** 的缩写，中文叫**统一资源定位符**。

简单说，它就是**互联网上某个资源的“地址”**。就像现实中你要找一栋房子需要知道它的门牌号，在网络上你要访问一个网页、一张图片、一个视频，就需要知道它的 URL。

一个典型的 URL 长这样：

text

https://www.example.com:443/path/page.html?name=abc&id=1#section2

它由几个部分组成：

|部分|示例|作用|
|---|---|---|
|协议| `https://` |用什么方式访问资源，常见的有 http、https、ftp|
|域名/主机| `www.example.com` |资源在哪台服务器上|
|端口| `:443` |服务器上的哪个“门”，通常省略（http 默认 80，https 默认 443）|
|路径| `/path/page.html` |服务器上资源的具体位置|
|查询参数| `?name=abc&id=1` |传给服务器的额外信息|
|片段| `#section2` |定位到页面内的某个位置|

**几个常见例子：**

- `https://www.baidu.com` —— 百度首页
    
- `https://www.bilibili.com/video/BV1xx411c7mD` —— 某个 B 站视频
    
- `https://github.com/user/repo` —— GitHub 上的一个仓库
    

所以，当你在浏览器地址栏里输入的东西，本质上就是一个 URL。它告诉浏览器：**去哪儿、用什么方式、取什么资源**
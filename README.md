webssh
====================


本人修改
------------

在原有功能基础上增加了，连接docker容器内部的功能,连接容器内部用的是entry，通过代码中entry.py启动了一个后台的容器连接客户端
在本工程webssh中添加了连接entry的功能

调用模式：webssh<->entryclient<->docker容器内部


entry 地址：https://github.com/laincloud/entry.git

Entry应用。负责如下工作：
    调用Docker Remote API
    通过WebSocket 传递stdin，stdout和stderr。
    根据protobuf3协议对各类消息进行序列化与反序列化。
    
-----------

WebSSH is a simple web project which support login linux server with explorer.

License: `MIT` (see LICENSE)

Information
-----------

> 1.git clone https://github.com/xsank/webssh.git

> 2.pip install paramiko && pip install tornado

> 3.python main.py

> 4.open your explorer and input your data then connect,the server init port is `9527`,
> you can modify it in `webssh.conf` file


Preview
-------
<div align="center">
    <img src="https://raw.githubusercontent.com/xsank/webssh/master/preview/webssh.png" width = "600" height = "377" alt="login" />
</div>
<div align="center">
    <img src="https://raw.githubusercontent.com/xsank/webssh/master/preview/cmd.png" width = "600" height = "295" alt="command" />
</div>
<div align="center">
    <img src="https://raw.githubusercontent.com/xsank/webssh/master/preview/top.png" width = "600" height = "297" alt="top" />
</div>
<div align="center">
    <img src="https://raw.githubusercontent.com/xsank/webssh/master/preview/vi.png" width = "600" height = "340" alt="vim" />
</div>


Others
------
To use CDN, the webssh use the version of term.js is `0.0.2`, you may update it with [new version](https://github.com/chjj/term.js).
And now the webssh support `linux` `mac` and `windows` OS.  
Please let me know if you meet any other problems.

Email:xsank#foxmail.com



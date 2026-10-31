# proxy-test
一个简单的代理测速工具

## 使用
请准备好[Python3.8+](https://www.python.org/downloads/)环境，下载本程序，运行即可。

### 参数说明

| 参数   | 默认值        | 说明         |
| ---- | ---------- | ---------- |
| `-p` | http       | 代理协议       |
| `-H` | 127.0.0.1  | 代理地址       |
| `-P` | 7890       | 代理端口       |
| `-u` | Google 204 | 测试网址，可重复指定 |
| `-n` | 10         | 总请求次数      |
| `-t` | 10         | 超时时间（秒）    |
| `-w` | 1          | 并发线程数      |

### 例子
默认测试：

```
python proxy_tester.py
```

自定义 HTTP 代理：

```
python proxy_tester.py \
    --proxy-protocol http \
    --proxy-host 127.0.0.1 \
    --proxy-port 7890
```

自定义测试次数和超时：

```
python proxy_tester.py -H 127.0.0.1 -P 7890 -n 100 -t 5
```

同时测试多个网站：

```
python proxy_tester.py \
    -u https://www.google.com/generate_204 \
    -u https://www.cloudflare.com \
    -u https://github.com \
    -n 30
```

并发测试：

```
python proxy_tester.py -n 100 -w 10 -t 5
```

## 许可证
[MIT](./LICENSE)
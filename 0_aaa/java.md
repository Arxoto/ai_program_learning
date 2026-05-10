# Java 基础

## 注解

todo

## 异常

- Error JVM 自己的异常
- Exception 编译时异常, 要求强制处理, 一般为外部因素导致
  - RuntimeException 运行时异常, 不要求强制处理

## 双亲委派模型

类加载器加载类时将请求给父类加载器去尝试加载, 防止修改核心类

## SPI Service-Provider-Interface

服务发现机制, 一个接口的具体实现可以在运行时动态加载, 经典用法就是 JDBC 驱动加载

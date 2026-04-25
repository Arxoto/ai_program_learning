# Spring

## Spring 重要模块

- 核心容器
  - spring-core
    - 提供框架最基础的工具，包括控制反转（IoC）与依赖注入（DI）的基础类、通用反射工具、资源抽象（Resource 接口）以及类型转换系统。
  - spring-beans
    - 实现 Bean 工厂与 Bean 定义解析，负责 Bean 的实例化、装配与生命周期管理。著名的 BeanFactory 接口即定义于此。
  - spring-context
    - 在 BeanFactory 之上构造 ApplicationContext，提供更丰富的容器特性：国际化（MessageSource）、事件发布（ApplicationEvent）、资源加载（ResourceLoader）等。
    - 同时引入了注解驱动的配置模型（@Component、@Autowired 等）。
  - spring-expression
    - Spring 表达式语言（SpEL）解析器，用于 @Value 注解、XML/注解中的动态表达式求值。

- 面向切面编程与切面集成
  - spring-aop
    - 基于代理的AOP实现。支持方法拦截与前置/后置/环绕等通知类型，是声明式事务、安全拦截等特性的底层基础。
  - spring-aspects
    - 与 AspectJ 的集成模块，允许使用 AspectJ 的完整切面表达式与编织能力。

- 数据访问与集成
  - spring-jdbc
    - 封装 JDBC API（`JdbcTemplate`）；定义统一的 `DataAccessException` 异常层次。
  - spring-tx
    - 声明式与编程式事务管理
  - spring-orm
    - 集成 Hibernate、JPA、JDO 等 ORM 框架
  - spring-oxm
    - 对象与 XML 映射支持
  - spring-jms
    - Java 消息服务集成（`JmsTemplate`），支持 ActiveMQ 消息中间件（ Kafka/RabbitMQ 在各自独立模块里）

- Web 层
  - spring-web
    - 基础 Web 集成功能，Rest客户端（`RestTemplate`）
  - spring-webmvc
    - Servlet 栈的 MVC 实现
  - spring-webflux
    - 响应式 Web 栈
  - spring-websocket
    - WebSocket协议支持

- 测试
  - spring-test
    - 提供单元测试与集成测试支持

- 消息处理
  - spring-messaging
    - 提供消息传递抽象，Message、MessageChannel、MessageHandler 等概念，不仅服务于 WebSocket，也支撑 Spring Cloud Stream 等外部项目。

## IoC 控制反转 & DI 依赖注入

**IoC（Inversion of Control，控制反转）** 是一种设计原则，其核心思想是将对象的创建、配置和生命周期管理的控制权，从调用方（业务代码）转移给外部容器。

优势
- 松耦合与可测试性（对象依赖接口）
- 生命周期与作用域统一管理（容器接管 Bean 的完整生命周期，并支持多种作用域）
- 代码简洁，聚焦业务逻辑
- 声明式服务集成（AOP的基础，事务、安全、缓存，不入侵业务代码）
- 灵活性与可扩展性（不修改代码，配置变更实现策略切换）

**DI（Dependency Injection，依赖注入）** 是实现 IoC 的具体手段。

Spring 中常见注入
- 构造函数注入（官方推荐）
- Setter 方法注入
- 字段注入（单测困难，用于测试类或快速原型）
- @Lookup 方法注入（用于解决单例 Bean 依赖原型 Bean 的场景）

## Spring Bean

**Spring Bean** 是由 Spring IoC 容器完成实例化、装配（依赖注入）并全生命周期管理的 Java 对象实例

Bean 在容器内部的元数据抽象 `BeanDefinition` （可由 XML 配置、注解驱动配置、编程式动态注册）

### Bean 的作用域 Scope

- singleton 单例，一个 IoC 容器仅存在一个实例
- prototype 原型，每次通过 `getBean()` 请求或依赖注入时，均创建全新实例。
- request 每个 HTTP 请求拥有独立实例
- session 每个 HTTP Session 拥有独立实例
- application 整个 ServletContext 级别单例，生命周期与 Web 应用一致
- websocket 每个 WebSocket 会话拥有一个独立实例

注意，
若将 prototype 作用域 Bean 注入到 singleton Bean 中，由于依赖注入仅在容器初始化时发生一次，会导致 prototype Bean 失去“每次获取均创建新实例”的特性。
解决方式是使用 方法注入（ @Lookup ） 或 ObjectFactory / Provider 。

### Bean 生命周期核心阶段

- 实例化
- 属性填充（装配）
- Aware 回调
  - Bean 能够感知到 beanName ，获取 `BeanFactory` 和 `ApplicationContext` 等
- 初始化前置处理
  - 实现 `BeanPostProcessor.postProcessBeforeInitialization()`
- 初始化
  - 执行顺序 `@PostConstruct`（推荐） -> `InitializingBean.afterPropertiesSet()` -> `init-method`
  - 用于资源预加载、连接建立等
- 初始化后置处理
  - 实现 `BeanPostProcessor.postProcessAfterInitialization()`
  - AOP 动态代理等
- 就绪
  - 放入 singletonObjects 一级缓存
- 销毁
  - 执行顺序 `@PreDestroy`（推荐） -> `DisposableBean.destroy()` -> `destroy-method`

### BeanFactory

BeanFactory 是 Spring IoC 容器的根接口，定义获取 Bean 实例、检查 Bean 存在性、获取 Bean 类型等方法

与其有关的类和易混淆的类

- ApplicationContext
  - 高级容器，继承并增强 BeanFactory ，提供了国际化、事件发布、资源加载、环境抽象、AOP 集成等企业级特性
  - BeanFactory 实例化时机是懒加载， ApplicationContext 是预实例化（容器启动时默认创建单例 Bean ）

- FactoryBean
  - 一个接口，用于定制复杂 Bean 创建逻辑的一种工厂 Bean

- ObjectFactory
  - 轻量级的函数式接口，用于解决循环依赖、注入延迟初始化对象、原型 Bean 的注入

## Spring 使用三级缓存解决循环依赖

**循环依赖**

循环依赖指两个 Bean 在创建过程中互相持有对方的引用，形成闭环。

在 Spring IoC 容器中，Bean 的创建通常经历实例化、属性填充（依赖注入）、初始化三个阶段。
若采用常规的单步创建流程，A 尚未创建完毕就需要注入 B，而 B 又需要注入 A，将导致无限递归或死锁。

因此，核心问题在于：在 Bean 尚未完全初始化时，向其依赖方暴露一个可用的引用，以打破创建僵局。

**三级缓存**

- 一级缓存 `singletonObjects`
  - 存储完全初始化的单例 Bean

- 二级缓存 `earlySingletonObjects`
  - 存储已实例化但尚未完成属性填充的 Bean

- 三级缓存 `singletonFactories`
  - 存储 `ObjectFactory<?>` ，可调用 `getObject()` 生成早期引用的工厂
  - 所有的 Bean 都必定会存入三级缓存，但只有涉及循环依赖的才会去从中获取，否则在初始化完成后直接存入一级缓存并在其他缓存中删除
  - 对于一个 Bean ，三级缓存只会被调用一次，之后会存入二级缓存中
  - AOP 场景下生成的是代理对象，非 AOP 场景获取的是原始对象

**AOP 代理场景与三级缓存的必要性**

若仅处理普通对象的循环依赖，二级缓存足以。

关键问题在于： Spring AOP 通常在 Bean 初始化后通过 `BeanPostProcessor` 的 `postProcessAfterInitialization` 生成代理对象并替换原始 Bean。
当存在循环依赖时，必须保证暴露给对方的引用就是最终代理对象，否则会出现注入原始对象的错误。

三级缓存中的 `ObjectFactory` 提前创建代理对象，用于正确的引用注入。
后续在正常的 `postProcessAfterInitialization` 生成代理对象过程中，通过 `earlyProxyReferences` 缓存判断是否提前生成，若已生成则不会重复生成。

**局限性**

三级缓存的设计，仅支持单例作用域下 Setter 注入或字段注入的循环依赖，无法解决构造器注入或原型作用域的循环依赖。

## AOP

AOP（Aspect-Oriented Programming，面向切面编程） 是一种编程范式，
旨在通过横向抽取机制，将散布于各模块中的横切关注点（Cross-cutting Concerns）（如日志记录、事务管理、权限校验、性能统计）与核心业务逻辑分离，并以切面（Aspect）的形式进行统一封装与管理。

**术语**

- 连接点 Join Point 可被拦截的特定点， Spring AOP 仅支持方法作为连接点
- 切入点 Pointcut 匹配连接点的表达式规则
- 通知 Advice 连接点上执行的增强逻辑
- 切面 Aspect 切入点与通知的集合

**Spring AOP**

Spring AOP 基于 **动态代理** 实现，属于 **运行时织入（Runtime Weaving）** ，与 AspectJ 的编译期/类加载期织入有本质区别。
- 编译期织入：需在 Maven/Gradle 构建中配置 AspectJ 编译器
- 类加载期织入：需修改 JVM 启动参数，引入 Java Agent

代理机制
- JDK 动态代理（ Spring Framework 的默认行为）
  - 基于 Java 反射机制，目标必须实现接口，代理对象转换为接口类型
  - 生成代理对象的开销较小，调用方法涉及反射
- CGLIB 代理（ SpringBoot 的默认代理策略）
  - 通过 ASM 字节码框架动态生成目标类的子类，无法代理 final 类、final 方法、private 方法
  - 生成代理对象的开销较大，方法调用性能通常优于 JDK 动态代理

通知类型
- 前置通知 `@Before` 方法执行前
- 后置返回通知 `@AfterReturning` 方法正常返回后
- 后置异常通知 `@AfterThrowing` 方法抛出异常后
- 最终通知 `@After` 方法结束，类似 finally 块
- 环绕通知 `@Around` 包围目标方法执行

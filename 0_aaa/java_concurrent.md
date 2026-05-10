# Java 多线程和并发

## 理论

死锁

- 互斥
- 占有并等待
- 不可抢占
- 循环等待

## Java 多线程

### volatile 关键字

JVM 保证了其可见性并防止指令重排, 常用于 Double-Checked Locking 模式

- 每次读写 volatile 变量都从主内存加载或刷新回去, 不经过线程的工作内存 (工作内存由 JMM 内存模型定义)
- 加入内存屏障以防止编译器和处理器进行指令重排

### synchronized 关键字

通过对象的监视器锁 (Monitor) 来实现

锁升级过程 (一般认为只会升级无法降级)

- 无锁: 对象刚创建出来, 还未被任何线程锁住
- 偏向锁: 认为一个线程持有锁后下一个大概率还是他, 在 jdk16 中被弃用
- 轻量级锁: 自旋锁, 假设锁会被立即释放, 让 CPU 空转一段时间, 自旋周期由 JVM 自调节
- 重量级锁: 自旋超过一定次数后就会升级, 进程进入阻塞状态, 由操作系统调度

### Object 原生的线程间协作的机制

以下都必须在 `synchronized` 中使用
- `wait()` 当前线程释放锁并进⼊阻塞状态, 直到被唤醒,
  - 需要在 `while (conditionNotMet)` 循环中使用以避免虚假唤醒, 条件根据业务自定义
- `notify()` 本对象的等待队列中随机唤醒一个
  - 若不满足唤醒条件则会再次 `wait()` 此时其他满足条件的线程就永远无法被唤醒, 这个条件是业务自定义的
- `notifyAll()` 唤醒所有对象

### 线程

线程的生命周期

- 新建 `NEW` 已创建但没 `start()`
- 可运⾏ `RUNNABLE` 调⽤了 `start()` 可能正在运行, 也可能等待 CPU 调度
- 阻塞 `BLOCKED` 等待 `synchronized` 锁释放, 若显式调用锁工具则为 `WAITING` 状态
- 等待 `WAITING` 线程调⽤了 `wait() ` / `join()` / `LockSupport.park()`
- 限期等待 `TIMED_WAITING` 调⽤带超时参数的等待⽅法
- 终⽌ `TERMINATED` 任务执⾏完毕, 或者抛出未捕获异常

创建多线程

- 继承 `Thread` 类, 不推荐, 因为不支持多继承
- 实现 `Runnable` 接口（无返回值）, 然后提交给 `Thread` 或线程池
- 若需要返回值, 使用 `Callable` （函数接口） + `FutureTask` （兼容层） 然后提交给线程
  - 线程池提交 `executorService.submit` 底层也是 `FutureTask`

异步任务
- `Future` 结果只能阻塞获取
- `CompletableFuture` 基于回调支持复杂调度/异常处理/聚合等

### 线程池

创建线程池

- 直接 `new ThreadPoolExecutor` （推荐方式, 等待队列选择有界队列）
- 使用 `Executors` 工厂类（不推荐）
  - `newFixedThreadpool` 固定线程池大小, 等待队列无界, 需要注意内存问题
  - `newCachedThreadPool` 弹性线程池, 无等待队列, 最大线程数 `Integer.MAX_VALUE` 不适应瞬间高并发
  - `newSingleThreadExecutor` 单线程 + 无界队列
  - `newScheduledThreadPool` 适合定时任务
- 分治线程池 `ForkJoinPool` 适用于纯计算任务
  - 每个线程有自己的双端队列存储任务, 新增任务加入到头部, 一个线程完成后会从其他线程的队列尾部窃取任务, 减少竞争

线程池关闭

- `shutdown()` 优雅关闭, 会等待当前队列的任务执行完毕, 同时拒绝任务提交
- `shutdownNow()` 强制关闭, 返回未开始的任务, 正在执行的任务抛出 `InterruptedException` 异常
  - 注意若 catch `InterruptedException`, 最后需要调用 `Thread.currentThread().interrupt();` 否则任务会继续往下跑

线程池线程数

- 若当前线程数小于核心线程数 则新建线程
- 若当前线程数等于核心线程数 则存入等待队列
- 若队列已满 且当前线程数小于最大线程数 则新建线程 临时线程可以被回收
- 若队列已满 且当前线程数等于最大线程数 则触发拒绝策略

线程池拒绝策略

- `AbortPolicy` 直接抛异常 `RejectedExecutionException`
- `CallerRunsPolicy` 谁提交谁处理
- `DiscardOldestPolicy` 丢弃最老的任务
- `DiscardPolicy` 直接丢弃新任务

线程池内部任务的异常处理

- 线程池内的任务, 如果没做特殊处理, 异常信息默认是打印到控制台的
- 手动加 try-catch , 这是最推荐的做法
- 继承 `ThreadPoolExecutor` , 覆盖 `afterExecute` ⽅法
- 通过 `executorService.submit` 提交后, 再 `future.get()` 拿到 ExecutionException (需要通过 `getCause()` 拿到原始异常)

## ThreadLocal

提供线程专属变量, 能够实现线程内数据共享 (无需传参)

底层原理

- `ThreadLocal` 存储的值是存在 `Thread` 对象中的
- 每个 `Thread` 对象中都存在属性 `ThreadLocal.ThreadLocalMap threadLocals` 来存储该线程的专属变量
  - 处理哈希冲突采用开放寻址法的线性探测
  - key 为不同的 `ThreadLocal` 对象, 使用弱引用 `WeakReference` 包裹, GC 会自动回收 (但是不回收 value )
  - value 是强引用, 在使用中若发现存在 key 为 null 的 value , 那么也会去清理, 但是不应依赖这个机制去避免内存泄漏
- 调用 `ThreadLocal::set` 的底层实现为
  - 通过 `Thread.currentThread()` 拿到当前线程
  - 然后 `map.set(this, value)` (这里的 this 就是 `ThreadLocal` 对象)

经典场景

- Web 应用的用户信息
- Spring 的事务管理

使用规范

- 数据隐式传递, 排查困难, 且会增加每个线程的内存开销, 不能滥用
- 线程池中会复用线程, 必须在 try-finally 中 remove 清理, 否则会有污染

### InheritableThreadLocal 可继承的

在父线程创建子线程时, 自动将 `inheritableThreadLocals` 里的数据拷贝一份 (浅拷贝), 做到父子线程继承数据

底层原理

- 侵入式的实现方式, 创建子线程 `new Thread()` 时, 通过 `Thread.currentThread()` 拿到父线程, 然后拷贝数据
- 浅拷贝, 因此之后父线程修改了, 子线程无法感知
- 线程池场景下可能继承到上⼀个任务的脏数据
  - 使用 Alibaba 的 `TransmittableThreadLocal`

### TransmittableThreadLocal 可传递的

任务提交到线程池时⾃动把当前线程的值拷⻉到⼦线程，等任务执⾏完再恢复

- 使用时需要用 `TtlExecutors.getTtlExecutorService()` 包装
- 或者传入 `TtlRunnable.get()` / `TtlCallable.get()` 生成的 `Runnable` / `Callable`

## JUC java.util.concurrent

### 线程安全的数据结构

历史遗留的线程安全的数据结构
- Vector / Hashtable , 方法为 synchronized , 性能较差
- Collections.synchronizedXxx 系列, 装饰器模式, 方法包一层 synchronized

JUC 下的数据结构
- ConcurrentHashMap 高吞吐 (jdk8 之前⽤ segment 分段锁, 之后是 CAS + synchronized 组合, 锁哈希桶的头节点)
- CopyOnWriteArrayList / CopyOnWriteArraySet 适合读多写少场景
- ArrayBlockingQueue / LinkedBlockingQueue 阻塞队列
- ConcurrentLinkedQueue 非阻塞高吞吐
- ConcurrentSkipListMap / ConcurrentSkipListSet 跳表原理, 元素自排序

阻塞队列

- ArrayBlockingQueue 有界队列, 读写共用锁, 内存可控, 少 GC
- LinkedBlockingQueue 支持有界/无界队列, 读写锁分开, 吞吐量大, 内存开销大
- SynchronousQueue 不存储元素, 生产后立即消费
- DelayQueue 元素必须实现 `Delayed` 接口, 到期取出
- PriorityBlockingQueue 无界优先级队列

### CAS

CAS (Compare-And-Swap) 一种原子操作的底层机制, 同时传入预期值和更新值, 仅当预期值与实际相符才进行修改, 否则返回失败

- 存在 ABA 问题, 无法感知中间是否被修改, 使用 `AtomicStampedReference` 带版本号解决
- 存在自旋开销, 竞争激烈时 CPU 占用高
- 仅保证单个变量的原子性

### 原子类

如 `AtomicLong` / `AtomicReference` 底层基于 CAS 实现无锁并发

另有专门的累加器 `LongAdder` 基于分段累加实现, 适用于写操作较多的场景, 但非强一致性

### AQS

AQS `AbstractQueuedSynchronizer` 是锁和同步器的底层基础
- 如 `ReentrantLock` 可重入锁, `Semaphore` 信号量, `CountDownLatch` 计数闭锁

底层原理

- 核心是一个 `volatile` 修饰的 int 类型的 state 来表示同步状态（不同实现含义不同）
- 线程通过 CAS 修改 state , 若成功则拿到资源, 若失败则进入等待队列
- 等待队列是双向链表, 一个节点代表一个线程

### 可重入锁 ReentrantLock

相比于 `synchronized` 关键字, 支持 超时等待 / 公平锁 / 条件等待 等高级能力

底层基于 AQS , 重入时 state + 1 , state 归零时释放锁

- 公平锁, AQS 调度时始终判断等待队列是否为空
- 非公平锁, AQS 锁释放时若下一个锁请求过来则直接获取到, 减少了线程切换的时间

### 信号量 Semaphore

控制并发度 适合做流控

### 计数闭锁 CountDownLatch

一次性的计数器 适合在主线程中做并发任务的完成等待

### 循环屏障 CyclicBarrier

同步器 适合并发协作中同步进度一起进入下一阶段

### 读写锁 ReentrantReadWriteLock

特性

- 写锁是排他的
- 读锁是共享的
- 写锁可以降级为读锁 读锁不能升级

注意

- 可能造成写饥饿, 此时可使用 `StampedLock` 支持乐观读, 代价是不可重入, 并且需要自己写乐观读悲观读逻辑
- 可开启公平锁防止饿死, 代价是开销大

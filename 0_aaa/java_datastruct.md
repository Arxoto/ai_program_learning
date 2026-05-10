# Java 数据结构

## Collection 集合

一般为 `List` / `Set` / `Queue` , 注意 `Map` 不是

### List

- ArrayList 基于数组实现
- LinkedList 基于链表实现
- CopyOnWriteArrayList 写时复制, 线程安全

ArrayList 扩容
- 初始容量 10
- 每次扩容 1.5 倍

### ConcurrentModificationException

集合遍历时若结构被修改则会报错 `ConcurrentModificationException`, 若要安全删除元素

- 迭代器方法 `Iterator::remove()` 可在迭代器循环中安全删除
- 集合方法 `Collection::removeIf()` 传入闭包, 底层就是迭代器方法, 部分类型如 ArrayList 做了性能优化
- 线程安全的类型都可以在遍历时删除

## Map

### HashMap / HashSet

HashSet 基于 HashMap 实现, 自定义 key 类型必须重写 `hashCode` 和 `equals` 方法

解决哈希碰撞采用拉链法 (拉出一个链表), 此外还有开放寻址法 (包括 线性探测 / ⼆次探测), `ThreadLocalMap` 就是线性探测
- key 计算 hash 后进行扰动运算, 异或低 16 位和高 16 位, 减少碰撞概率
- 数组下标计算是通过 `hash & (capacity - 1)` 计算, 要求容量必须是 2^n 时才等价于取模

底层是 数组 + 链表/红黑树
- 数组初始长度 16 , 负载因子 0.75 , 如第一次到 `16 * 0.75 = 12` 则扩容, 扩容容量始终翻倍 (为了哈希运算)
- 链表长度超过 8 且数组长度小于 64 则优先扩容数组
- 链表长度超过 8 且数组长度大于 64 则转换成红黑树
- 数大小小于 6 则转回列表

### ConcurrentHashMap

HashMap 支持 key 或 value 为 null , ConcurrentHashMap 两者均不支持

避免多线程下的歧义, `containsKey` 和 `get` 之间不是原子的

### LinkedHashMap

是 HashMap 的子类, 额外维护双向链表, 维护插入顺序或者访问顺序

### TreeMap

即 **红黑树** 的有序 Map 实现, 一种自平衡二叉查找树


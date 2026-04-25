# Spring DB

## Spring 事务隔离

使用 `@Transactional` 注解的方法，其内部的所有 SQL 共享同一个数据库事务，异常自动回滚。
本质是封装 JDBC 连接级别设置，由数据库提供隔离性，但提供了抽象层与具体数据库解耦。

级别与对应 JDBC 中的隔离级别
- ISOLATION_DEFAULT 使用数据库默认隔离级别
- ISOLATION_READ_UNCOMMITTED 读未提交
- ISOLATION_READ_COMMITTED 读已提交
- ISOLATION_REPEATABLE_READ 可重复读
- ISOLATION_SERIALIZABLE 可串行化

事务隔离级别
- 读未提交
  - 一个事务可以读取另一个未提交事务的修改
  - 允许脏读、不可重复读、幻读
- 读已提交
  - 一个事务只能读取其他事务已经提交的数据
  - 防止脏读，但存在不可重复读、幻读
- 可重复读
  - 事务内多次读取同一行数据，结果保持一致，不受其他事务提交的影响
  - 防止脏读、不可重复读，但可能存在幻读
- 可串行化
  - 事务完全串行执行
  - 防止脏读、不可重复读、幻读

名词解释
- 脏读：读到其他事务可能回退的数据
- 不可重复读：同一事务内两次相同的查询，如果中间有其他事务提交了修改，第二次会看到不同的结果
- 禁止不可重复读：事务开始时建立一致性快照（MVCC）或持有行锁，保证同一查询结果不变
- 幻读：同一事务内两次相同的查询，如果中间有其他事务提交了插入，第二次会看到多的数据

在 **可重复读** 级别下，若基于 SELECT 的结果去 UPDATE 更新数据，可能使其他事务的更新丢失。解决方案如下：
- 悲观锁：对该行施加 **排他锁** ，直至事务提交或回滚， `SELECT ... FOR UPDATE`
- 乐观锁：添加 version 字段，更新时增加 version 条件来保证版本一致，失败需要重试
- 原子更新：适用于简单运算场景， `UPDATE xx SET x = x - 1`
- 升级隔离级别至 SERIALIZABLE 可串行化

DB 锁介绍
- 共享锁，允许多个事务持有，并发读、写阻塞 `SELECT ... LOCK IN SHARE MODE` / `SELECT ... FOR SHARE`
- 排他锁，只允许一个事务持有， UPDATE/DELETE 自动加锁， SELECT 手动加锁 `SELECT ... FOR UPDATE`

MySQL InnoDB 的行锁算法
- 记录锁 Record Lock ，锁住单个索引记录，阻止其他事务修改/删除该记录
- 间隙锁 Gap Lock ，锁住索引记录之间的间隙，阻止向间隙中插入新记录，在可重复读级别下极大程度避免了幻读（不加锁的快照读不保证）
- 临键锁 Next-Key Lock ，即 记录锁+间隙锁

## todo Spring 有哪几种事务传播行为?Spring 事务传播行为有什么用?

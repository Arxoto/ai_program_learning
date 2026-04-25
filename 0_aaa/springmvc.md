# SpringMVC

## Spring MVC

Spring MVC 是 Spring 框架中用于构建 Web 应用的模块，基于 MVC (Model-View-Controller) 设计模式。
围绕 `DispatcherServlet` 前端控制器，实现请求路由、数据绑定、视图渲染

- 请求到达 `DispatcherServlet`
- 遍历 `HandlerMapping` 查找 Handler （通常为 Controller 中的方法）
- 应用拦截器前置 `preHandle` 方法，任意返回 `false` 表示中止
- 调用 `HandlerAdapter` 执行具体的处理器方法，返回 `ModelAndView`
- 应用拦截器后置 `postHandle` 方法
- 通过 `ViewResolver` 解析逻辑视图名得到 `View` 对象，进行数据填充并渲染
- 完成拦截器，调用拦截器的 `afterCompletion` 方法

当使用 `@RestController` 时，移除视图解析与渲染阶段，且 `postHandle` 拦截器无法修改响应体（因为已经写入响应体）

## Filter & HandlerInterceptor

Filter 是 Servlet 容器级，对所有进入 Servlet 容器的请求生效，操作 ServletRequest / ServletResponse / FilterChain ，通过 `chain.doFilter()` 进入下一个 `Filter`

HandlerInterceptor 是 Spring MVC 框架级，作用于 `DispatcherServlet` 匹配到 Handler 的请求，有三个独立回调： `preHandle`、`postHandle`、`afterCompletion`

Filter 先于 HandlerInterceptor 执行

## Spring MVC 父子容器

**在 Spring Boot 中已不常用**

- 父容器（Root WebApplicationContext）：由 `ContextLoaderListener` 加载，通常管理 Service、Dao、数据源、事务管理器 等非 Web 层的基础组件。
- 子容器（Servlet WebApplicationContext）：由 `DispatcherServlet` 加载，通常管理 Controller（`@Controller`）、视图解析器（ViewResolver）、HandlerMapping、拦截器 等 Web 层专属组件。


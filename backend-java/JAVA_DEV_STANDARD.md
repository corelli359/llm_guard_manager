# 代码规范

```
使用的技术栈：mysql8.x、mybatis-plus、jdk8、springboot2.x、springsecurity、jwt、maven
```


## 一、命名规范

- **布尔类型变量**：禁止使用 `isXxx` 命名（POJO 中 getter 会生成 `isIsXxx`），应使用 `deleted`、`enabled` 等
- **Service接口及实现类**：接口使用`I`开头，如IUserService；实现类使用 `Impl` 后缀，如 `UserServiceImpl`
- **数据库相关**：`Mapper` 后缀对应 MyBatis的Mapper接口
- **VO/DTO/DO**：明确标注对象用途，如Controller接口接收到的对象以VO结尾，表对象用DO结尾



## 二、注释规范

### 2.1 文件头（必须）

```java
/**
 * 软件著作权：XXXXX研发中心
 *
 * @date 2024/07/13 16:06
 */
```



### 2.2 类注释（必须）

```java
/**
 * 功能描述：用户服务接口，提供用户基本信息管理功能
 *
 * @date 2024/07/13 16:06
 */
public class UserService { ... }
```

### 2.3 方法注释（必须）

```java
/**
 * 根据用户ID查询用户信息
 *
 * @param userId 用户ID，不能为空
 * @return 用户信息对象，不存在时返回 null
 * @throws BusinessException 当用户ID格式不合法时抛出
 */
public User getUserById(Long userId) { ... }
```

### 2.4 行内注释

- 行内注释（`//`）与代码之间必须有空格：如`// 首先执行sql查询`

## 三、Controller统一返回格式

```java
public class R{
    private boolean success;
    private int code;
    private String msg;
    private Object data;
}
```


## 四、安全编码规范

### 4.1 SQL 注入防护【高危】

```java
// 禁止 Mapper.xml 中使用 ${} 拼接（高危漏洞）
SELECT * FROM user WHERE name = ${name}

// Mapper.xml 统一使用 #{} 预编译占位符
SELECT * FROM user WHERE name = #{name}

// 禁止 手动拼接 LIKE（仍有注入风险）
.apply("name LIKE '%" + keyword + "%'")

// 正确 需要 LIKE 模糊查询时，使用内置方法而非手拼 %
userMapper.selectList(
    new LambdaQueryWrapper()
        .like(User::getName, keyword)  // 自动处理 % 转义，防止注入
);

// 禁止 直接将前端传入字段名用于排序
@Select("SELECT * FROM user ORDER BY ${sortField}")

// 正确 白名单校验后再使用
private static final Set ALLOWED_SORT_FIELDS =
    Set.of("create_time", "user_name", "age");

public List listSorted(String sortField) {
    if (!ALLOWED_SORT_FIELDS.contains(sortField)) {
        throw new BusinessException("非法排序字段");
    }
    return userMapper.selectList(
        new LambdaQueryWrapper().last("ORDER BY " + sortField)
    );
}
```

### 4.2 XSS 防护【高危】

- 所有从外部输入的数据（请求参数、表单、URL参数）在输出到页面前必须进行 HTML 转义
- 使用 Apache Commons Text 的 `StringEscapeUtils.escapeHtml4()` 进行转义
- 禁止直接将用户输入拼接到 HTML/JS 代码中

### 4.3 敏感信息保护【高危】

```java
// 禁止 - 硬编码密码/密钥
String password = "admin123";
String secretKey = "mySecretKey12345";

// 正确 - 从配置文件或环境变量读取
@Value("${app.secret.key}")
private String secretKey;
```

- 日志中禁止打印密码、身份证号、银行卡号、手机号等敏感字段
- 接口响应中敏感字段必须脱敏（手机号：`138****8888`，身份证：前6后4）


### 4.4 路径遍历防护【高危】

```java
// 禁止 - 直接使用用户输入构造文件路径
File file = new File("/upload/" + fileName);

// 正确 - 校验并规范化路径
String safeFileName = Paths.get(fileName).getFileName().toString();
File file = new File("/upload/", safeFileName);
if (!file.getCanonicalPath().startsWith("/upload/")) {
    throw new SecurityException("非法文件路径");
}
```

### 4.5 命令注入防护【高危】

```java
// 禁止 - 直接将用户输入传入 Runtime.exec()
Runtime.getRuntime().exec("ping " + userInput);

// 正确 - 参数列表方式，避免 shell 注入
String[] cmd = {"ping", "-c", "4", validatedHost};
ProcessBuilder pb = new ProcessBuilder(cmd);
// 并严格白名单校验 validatedHost
```

### 4.6 SSRF 防护【高危】

- 禁止直接使用用户传入的 URL 发起 HTTP 请求
- 必须对目标 URL 进行白名单校验（域名/IP 范围）
- 禁止访问内网 IP 段：`10.x.x.x`、`172.16-31.x.x`、`192.168.x.x`、`127.0.0.1`

### 4.7 随机数安全

```java
// 禁止 - 使用 java.util.Random（可预测）用于安全场景
Random random = new Random();
String token = String.valueOf(random.nextInt());

// 正确 - 安全场景使用 SecureRandom
SecureRandom secureRandom = new SecureRandom();
byte[] tokenBytes = new byte[32];
secureRandom.nextBytes(tokenBytes);
```


## 五、异常处理规范

### 5.1 异常捕获规则

- 禁止捕获 `Exception` 或 `Throwable` 然后直接忽略（空 catch 块）
- 捕获的异常必须处理：记录日志或向上抛出，至少做其中一件
- 禁止在 catch 中使用 `e.printStackTrace()`，必须使用日志框架（SLF4J + Logback）
- 不要用异常控制正常业务流程
- `finally` 块中禁止使用 `return` 语句
- 使用spring的全局异常处理器兜底

```java
// 禁止 - 吞掉异常
try {
    doSomething();
} catch (Exception e) {
    // 什么都不做
}

// 正确
try {
    doSomething();
} catch (IOException e) {
    log.error("操作失败: {}", e.getMessage(), e);
    throw new BusinessException("操作失败", e);
}
```

### 5.2 自定义异常规范

- 业务异常继承 `RuntimeException`，命名以 `Exception` 结尾
- 异常类必须包含 `code`（错误码）和 `msg`（错误描述）

### 5.3 资源关闭

所有 IO 资源（`Connection`、`Stream`、`Reader` 等）必须在 finally 中关闭，或使用 try-with-resources。

```java
// 推荐 - try-with-resources 自动关闭
try (Connection conn = dataSource.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    // 执行操作
} catch (SQLException e) {
    log.error("数据库操作失败", e);
}
```


## 六、并发与线程安全规范

### 6.1 线程池规范

- 必须使用 `ThreadPoolExecutor` 显式指定核心线程数、最大线程数、队列容量、拒绝策略
- 线程池必须命名（使用 `ThreadFactory` 设置线程名），便于排查问题

```java
// 正确创建方式
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    5,                               // 核心线程数
    20,                              // 最大线程数
    60L, TimeUnit.SECONDS,           // 空闲线程存活时间
    new LinkedBlockingQueue<>(200),  // 有界队列
    new ThreadFactoryBuilder().setNameFormat("order-pool-%d").build(),
    new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略
);
```


## 七、日志规范

### 7.1 日志框架

- 统一使用 **SLF4J 门面 + Logback** 实现，禁止使用 `System.out.println` 输出业务日志
- Logger 对象必须为 `private static final`，类型为 `org.slf4j.Logger`

```java
private static final Logger log = LoggerFactory.getLogger(UserService.class);

// 使用占位符，避免字符串拼接（性能更好，且不在 DEBUG 关闭时计算）
log.info("用户登录成功，userId={}, ip={}", userId, ip);

// 禁止字符串拼接
log.info("用户登录成功，userId=" + userId + ", ip=" + ip);
```

### 7.2 日志禁止行为

- 禁止记录密码、证件号、银行卡号等敏感信息
- 禁止在循环中每次打印日志（可能造成日志洪泛）
- 禁止在生产环境使用 DEBUG 级别全量输出
- 异常日志必须包含完整堆栈：`log.error("描述", e)`，不要只记录 `e.getMessage()`


## 八、数据校验规范

### 8.1 输入校验原则

- Controller 层输入的VO对象使用 Validation（`@NotNull`、`@NotBlank`、`@Size`、`@Pattern` 等）
- 数值类型必须校验范围（防止极大值、负数等异常输入）
- 字符串类型必须校验长度


## 九、数据库操作规范

### 9.1 SQL 编写规范

- 禁止使用 `SELECT *`，必须明确列出所需字段
- 批量操作必须限制每批数量（建议 500 条以内），防止大事务
- 更新和删除操作必须带 `WHERE` 条件，禁止全表更新/删除
- 禁止在代码中进行大表 JOIN（超百万行），应在数据库设计层解决
- 所有 SQL 必须有对应索引支持，禁止全表扫描高频查询

### 9.2 事务规范

- 事务范围尽量小，避免长事务（不要在事务中进行 HTTP 调用等耗时操作）
- `@Transactional` 注解必须明确指定 `rollbackFor` 属性
- 同一个类中的方法调用不走 Spring 代理，`@Transactional` 不生效，需注意

```java
// 正确
@Transactional(rollbackFor = Exception.class)
public void createOrder(OrderDTO dto) {
    // 只做数据库操作
}
```

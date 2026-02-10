# 使用分层构建减小镜像体积
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY target/*.jar app.jar
# 针对 Minikube 的极简 JVM 参数
# -XX:MaxRAMPercentage=75.0: 自动适配容器内存限制
# -XX:+UseSerialGC: 单核/低内存环境下 SerialGC 开销最小
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75.0 -XX:+UseSerialGC -Djava.security.egd=file:/dev/./urandom"
EXPOSE 9001
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]

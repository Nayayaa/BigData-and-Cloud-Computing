FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -q -e -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
ENV SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/hotel
ENV SPRING_DATASOURCE_USERNAME=hotel_user
ENV SPRING_DATASOURCE_PASSWORD=hotel_pass
ENV SPRING_DATASOURCE_DRIVER=org.postgresql.Driver
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]

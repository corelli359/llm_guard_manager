package com.llmguard.manager.service;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class UsapClient {

    private final RestClient.Builder restClientBuilder;

    @Value("${app.usap.base-url}")
    private String baseUrl;

    @Value("${app.usap.client-id}")
    private String clientId;

    @Value("${app.usap.client-secret}")
    private String clientSecret;

    public UsapClient(RestClient.Builder restClientBuilder) {
        this.restClientBuilder = restClientBuilder;
    }

    private RestClient buildClient() {
        return restClientBuilder.baseUrl(baseUrl).build();
    }

    public UsapValidationResult validateTicket(String ticket) {
        try {
            return buildClient()
                    .post()
                    .uri("/api/auth/validate-ticket")
                    .header("X-Client-ID", clientId)
                    .header("X-Client-Secret", clientSecret)
                    .body(Map.of("ticket", ticket))
                    .retrieve()
                    .body(UsapValidationResult.class);
        } catch (Exception e) {
            log.error("Failed to validate ticket with USAP", e);
            throw new RuntimeException("USAP service error: " + e.getMessage());
        }
    }

    public UsapUserInfo getUserInfo(String userId) {
        try {
            return buildClient()
                    .get()
                    .uri("/api/users/{userId}", userId)
                    .header("X-Client-ID", clientId)
                    .header("X-Client-Secret", clientSecret)
                    .retrieve()
                    .body(UsapUserInfo.class);
        } catch (Exception e) {
            log.error("Failed to get user info from USAP for userId={}", userId, e);
            throw new RuntimeException("USAP service error: " + e.getMessage());
        }
    }

    @SuppressWarnings("unchecked")
    public UsapBatchUsersResult getUsersBatch(List<String> userIds) {
        try {
            return buildClient()
                    .post()
                    .uri("/api/users/batch")
                    .header("X-Client-ID", clientId)
                    .header("X-Client-Secret", clientSecret)
                    .body(Map.of("user_ids", userIds))
                    .retrieve()
                    .body(UsapBatchUsersResult.class);
        } catch (Exception e) {
            log.error("Failed to batch fetch users from USAP", e);
            throw new RuntimeException("USAP service error: " + e.getMessage());
        }
    }

    public UsapHealthResult healthCheck() {
        try {
            return buildClient()
                    .get()
                    .uri("/api/health")
                    .retrieve()
                    .body(UsapHealthResult.class);
        } catch (Exception e) {
            log.error("USAP health check failed", e);
            throw new RuntimeException("USAP service error: " + e.getMessage());
        }
    }

    @Data
    public static class UsapValidationResult {
        private boolean valid;
        @JsonProperty("user_id")
        private String userId;
        @JsonProperty("user_name")
        private String userName;
        private String email;
        private String department;
        private String error;
    }

    @Data
    public static class UsapUserInfo {
        @JsonProperty("user_id")
        private String userId;
        @JsonProperty("user_name")
        private String userName;
        private String email;
        private String department;
        @JsonProperty("display_name")
        private String displayName;
    }

    @Data
    public static class UsapBatchUsersResult {
        private List<UsapUserInfo> users;
        @JsonProperty("not_found")
        private List<String> notFound;
    }

    @Data
    public static class UsapHealthResult {
        private String status;
        private String service;
    }
}

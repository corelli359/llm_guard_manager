package com.llmguard.manager.controller;

import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.repository.UserRepository;
import com.llmguard.manager.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequiredArgsConstructor
public class AuthController {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;

    private static final String HARDCODED_ADMIN_USERNAME = System.getenv("ADMIN_USERNAME") != null ? System.getenv("ADMIN_USERNAME") : "admin";
    private static final String HARDCODED_ADMIN_PASSWORD = System.getenv("ADMIN_PASSWORD") != null ? System.getenv("ADMIN_PASSWORD") : "changeme";

    @PostMapping(value = "/login/access-token", consumes = MediaType.APPLICATION_FORM_URLENCODED_VALUE)
    public ResponseEntity<Map<String, Object>> login(
            @RequestParam String username,
            @RequestParam String password
    ) {
        // 1. Check hardcoded admin
        if (HARDCODED_ADMIN_USERNAME.equals(username) && HARDCODED_ADMIN_PASSWORD.equals(password)) {
            Optional<User> adminUser = userRepository.findByUsername(username);
            User user = adminUser.orElseGet(() -> {
                User newAdmin = User.builder()
                        .id(java.util.UUID.randomUUID().toString())
                        .username(HARDCODED_ADMIN_USERNAME)
                        .hashedPassword(passwordEncoder.encode(HARDCODED_ADMIN_PASSWORD))
                        .role("SYSTEM_ADMIN")
                        .isActive(true)
                        .createdAt(java.time.LocalDateTime.now())
                        .build();
                return userRepository.save(newAdmin);
            });

            String token = jwtService.generateToken(user);
            Map<String, Object> response = new HashMap<>();
            response.put("access_token", token);
            response.put("token_type", "bearer");
            response.put("role", user.getRole());
            return ResponseEntity.ok(response);
        }

        // 2. Fallback to database user
        Optional<User> dbUser = userRepository.findByUsername(username);
        if (dbUser.isEmpty()) {
            return ResponseEntity.status(401).body(Map.of("detail", "Incorrect username or password"));
        }

        User user = dbUser.get();
        if (!user.getIsActive()) {
            return ResponseEntity.status(403).body(Map.of("detail", "Inactive user"));
        }

        if (!passwordEncoder.matches(password, user.getHashedPassword())) {
            return ResponseEntity.status(401).body(Map.of("detail", "Incorrect username or password"));
        }

        String token = jwtService.generateToken(user);
        Map<String, Object> response = new HashMap<>();
        response.put("access_token", token);
        response.put("token_type", "bearer");
        response.put("role", user.getRole());
        return ResponseEntity.ok(response);
    }
}

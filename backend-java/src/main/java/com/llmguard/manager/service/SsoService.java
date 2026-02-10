package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.SsoLoginResponse;
import com.llmguard.manager.domain.entity.User;
import com.llmguard.manager.repository.UserRepository;
import com.llmguard.manager.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime; // 注意：原代码导入错误，已修正
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class SsoService {

    private final UsapClient usapClient;
    private final UserRepository userRepository;
    private final JwtService jwtService;

    @Value("${app.security.jwt.expiration}")
    private long jwtExpiration;

    @Transactional
    public SsoLoginResponse loginWithTicket(String ticket) {
        // 1. 验证 Ticket
        UsapClient.UsapValidationResult validation = usapClient.validateTicket(ticket);
        
        if (!validation.isValid()) {
            throw new IllegalArgumentException("Invalid ticket: " + validation.getError());
        }

        // 2. 同步用户
        User user = syncUser(validation);

        // 3. 生成 Token
        String token = jwtService.generateToken(user);

        return SsoLoginResponse.builder()
                .accessToken(token)
                .tokenType("Bearer")
                .expiresIn(jwtExpiration)
                .userId(user.getUserId())
                .role(user.getRole())
                .build();
    }

    private User syncUser(UsapClient.UsapValidationResult validation) {
        // 先按 userId 查找，再按 username 查找
        return userRepository.findByUserId(validation.getUserId())
                .or(() -> userRepository.findByUsername(validation.getUserId()))
                .map(existingUser -> {
                    existingUser.setDisplayName(validation.getUserName());
                    existingUser.setEmail(validation.getEmail());
                    existingUser.setUpdatedAt(LocalDateTime.now());
                    return userRepository.save(existingUser);
                })
                .orElseGet(() -> {
                    User newUser = User.builder()
                            .id(UUID.randomUUID().toString())
                            .userId(validation.getUserId())
                            .username(validation.getUserId())
                            .hashedPassword("")
                            .displayName(validation.getUserName())
                            .email(validation.getEmail())
                            .role("ANNOTATOR")
                            .isActive(true)
                            .createdAt(LocalDateTime.now())
                            .build();
                    return userRepository.save(newUser);
                });
    }
}

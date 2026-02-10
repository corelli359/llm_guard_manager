package com.llmguard.manager.domain.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class SsoBatchUsersResponse {
    private List<SsoUserInfoResponse> users;
    private List<String> notFound;
}

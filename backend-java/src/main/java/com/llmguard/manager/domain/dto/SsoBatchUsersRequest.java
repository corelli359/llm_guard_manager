package com.llmguard.manager.domain.dto;

import lombok.Data;

import java.util.List;

@Data
public class SsoBatchUsersRequest {
    private List<String> userIds;
}

package com.llmguard.manager.service;

import com.llmguard.manager.domain.dto.ScenarioCreate;
import com.llmguard.manager.domain.dto.ScenarioUpdate;
import com.llmguard.manager.domain.entity.Scenario;
import com.llmguard.manager.repository.ScenarioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ScenarioService {

    private final ScenarioRepository scenarioRepository;

    public List<Scenario> getAllScenarios() {
        return scenarioRepository.findAll();
    }

    public Scenario getScenarioByAppId(String appId) {
        return scenarioRepository.findByAppId(appId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Scenario not found"));
    }

    public Scenario getScenario(String id) {
        return scenarioRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Scenario not found"));
    }

    @Transactional
    public Scenario createScenario(ScenarioCreate dto) {
        if (scenarioRepository.existsByAppId(dto.getAppId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "App ID already exists");
        }

        Scenario scenario = Scenario.builder()
                .id(UUID.randomUUID().toString())
                .appId(dto.getAppId())
                .appName(dto.getAppName())
                .description(dto.getDescription())
                .isActive(true)
                .enableWhitelist(dto.getEnableWhitelist() != null ? dto.getEnableWhitelist() : true)
                .enableBlacklist(dto.getEnableBlacklist() != null ? dto.getEnableBlacklist() : true)
                .enableCustomPolicy(dto.getEnableCustomPolicy() != null ? dto.getEnableCustomPolicy() : true)
                .build();

        return scenarioRepository.save(scenario);
    }

    @Transactional
    public Scenario updateScenario(String id, ScenarioUpdate dto) {
        Scenario scenario = getScenario(id);

        if (dto.getAppName() != null) {
            scenario.setAppName(dto.getAppName());
        }
        if (dto.getDescription() != null) {
            scenario.setDescription(dto.getDescription());
        }
        if (dto.getIsActive() != null) {
            scenario.setIsActive(dto.getIsActive());
        }
        if (dto.getEnableWhitelist() != null) {
            scenario.setEnableWhitelist(dto.getEnableWhitelist());
        }
        if (dto.getEnableBlacklist() != null) {
            scenario.setEnableBlacklist(dto.getEnableBlacklist());
        }
        if (dto.getEnableCustomPolicy() != null) {
            scenario.setEnableCustomPolicy(dto.getEnableCustomPolicy());
        }

        return scenarioRepository.save(scenario);
    }

    @Transactional
    public void deleteScenario(String id) {
        Scenario scenario = getScenario(id);
        scenarioRepository.delete(scenario);
    }
}

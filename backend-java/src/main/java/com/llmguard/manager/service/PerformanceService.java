package com.llmguard.manager.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.llmguard.manager.domain.dto.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.io.IOException;
import java.nio.file.*;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
@Service
public class PerformanceService {

    private static final String GUARDRAIL_SERVICE_URL = "http://127.0.0.1:8000/api/input/instance/rule/run";
    private static final String HISTORY_DIR = "performance_history";
    private static final DateTimeFormatter ISO_FMT = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    private final ObjectMapper objectMapper;
    private final RestClient restClient;
    private final ExecutorService executor = Executors.newCachedThreadPool();

    // --- Mutable test state (guarded by volatile / atomic) ---
    private volatile boolean running = false;
    private final AtomicBoolean shouldStop = new AtomicBoolean(false);
    private volatile String testId;
    private volatile long startTimeMs;
    private volatile long endTimeMs;
    private volatile int currentUsers;

    // History buffer (time-series data points for the current/last test)
    private final CopyOnWriteArrayList<Map<String, Object>> historyBuffer = new CopyOnWriteArrayList<>();

    // Current test config references
    private volatile GuardrailConfig targetConfig;
    private volatile PerformanceTestStartRequest testConfig;

    // Stats - use atomics for thread safety
    private final AtomicLong totalRequests = new AtomicLong();
    private final AtomicLong successRequests = new AtomicLong();
    private final AtomicLong errorRequests = new AtomicLong();
    private final AtomicLong latencySumMs = new AtomicLong(); // sum of successful latencies in ms
    private final AtomicLong latencyCount = new AtomicLong(); // count of successful requests (for avg)

    // Window stats for RPS / percentile calculation
    private final AtomicLong windowRequests = new AtomicLong();
    private final AtomicLong windowErrors = new AtomicLong();
    private volatile long windowStartMs = System.currentTimeMillis();
    private final CopyOnWriteArrayList<Double> windowLatencies = new CopyOnWriteArrayList<>();

    // Last computed metrics (updated each window)
    private volatile double lastRps = 0.0;
    private volatile double lastErrorRps = 0.0;
    private volatile double lastP95 = 0.0;
    private volatile double lastP99 = 0.0;

    public PerformanceService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
        this.restClient = RestClient.create();
        Path dir = Paths.get(HISTORY_DIR);
        if (!Files.exists(dir)) {
            try {
                Files.createDirectories(dir);
            } catch (IOException e) {
                log.warn("Failed to create history directory", e);
            }
        }
    }

    // ======================== Dry Run ========================

    public PerformanceDryRunResponse dryRun(GuardrailConfig config) {
        Map<String, Object> payload = buildPayload(config);
        long start = System.currentTimeMillis();
        try {
            String body = restClient.post()
                    .uri(GUARDRAIL_SERVICE_URL)
                    .header("Content-Type", "application/json")
                    .body(payload)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (req, resp) -> {
                        // do not throw, we handle below
                    })
                    .body(String.class);

            long latency = System.currentTimeMillis() - start;
            Object data = objectMapper.readValue(body, Object.class);
            return PerformanceDryRunResponse.builder()
                    .success(true)
                    .latency(latency)
                    .data(data)
                    .build();
        } catch (Exception e) {
            long latency = System.currentTimeMillis() - start;
            return PerformanceDryRunResponse.builder()
                    .success(false)
                    .latency(latency)
                    .error(e.getMessage())
                    .build();
        }
    }

    // ======================== Start / Stop ========================

    public boolean isRunning() {
        return running;
    }

    public void startTest(PerformanceTestStartRequest request) {
        if (running) {
            throw new IllegalStateException("A performance test is currently running.");
        }

        // Reset state
        resetStats();
        this.targetConfig = request.getTargetConfig();
        this.testConfig = request;
        this.testId = UUID.randomUUID().toString();
        this.startTimeMs = System.currentTimeMillis();
        this.endTimeMs = 0;
        this.currentUsers = 0;
        this.running = true;
        this.shouldStop.set(false);

        // Run in background
        executor.submit(() -> {
            try {
                String type = request.getTestType();
                if ("FATIGUE".equalsIgnoreCase(type) && request.getFatigueConfig() != null) {
                    runFatigue(request.getFatigueConfig().getConcurrency(),
                            request.getFatigueConfig().getDuration());
                } else if ("STEP".equalsIgnoreCase(type) && request.getStepConfig() != null) {
                    StepLoadConfig sc = request.getStepConfig();
                    runStep(sc.getInitialUsers(), sc.getStepSize(),
                            sc.getStepDuration(), sc.getMaxUsers());
                }
            } catch (Exception e) {
                log.error("Test execution error", e);
            } finally {
                running = false;
                if (endTimeMs == 0) {
                    endTimeMs = System.currentTimeMillis();
                }
                snapshotHistory(System.currentTimeMillis(), lastRps, lastErrorRps, lastP95, lastP99);
                saveHistory();
                currentUsers = 0;
            }
        });
    }

    public void stopTest() {
        shouldStop.set(true);
        running = false;
        endTimeMs = System.currentTimeMillis();
    }

    public PerformanceStatusResponse getStatus() {
        long now = System.currentTimeMillis();
        int duration;
        if (running) {
            duration = (int) ((now - startTimeMs) / 1000);
        } else if (endTimeMs > 0) {
            duration = (int) ((endTimeMs - startTimeMs) / 1000);
        } else {
            duration = 0;
        }

        double rps = lastRps;
        double errorRps = lastErrorRps;
        double p95 = lastP95;
        double p99 = lastP99;

        double windowDuration = (now - windowStartMs) / 1000.0;
        if (windowDuration >= 1.0) {
            rps = windowRequests.get() / windowDuration;
            errorRps = windowErrors.get() / windowDuration;

            List<Double> latencies = new ArrayList<>(windowLatencies);
            if (!latencies.isEmpty()) {
                Collections.sort(latencies);
                p95 = percentile(latencies, 0.95);
                p99 = percentile(latencies, 0.99);
            } else {
                p95 = 0.0;
                p99 = 0.0;
            }

            lastRps = rps;
            lastErrorRps = errorRps;
            lastP95 = p95;
            lastP99 = p99;

            snapshotHistory(now, rps, errorRps, p95, p99);
            windowStartMs = now;
            windowRequests.set(0);
            windowErrors.set(0);
            windowLatencies.clear();
        }

        double avgLat = 0.0;
        if (latencyCount.get() > 0) {
            avgLat = (double) latencySumMs.get() / latencyCount.get();
        }

        int histSize = historyBuffer.size();
        List<Map<String, Object>> tail = histSize > 60
                ? new ArrayList<>(historyBuffer.subList(histSize - 60, histSize))
                : new ArrayList<>(historyBuffer);

        return PerformanceStatusResponse.builder()
                .isRunning(running)
                .duration(duration)
                .currentUsers(currentUsers)
                .totalRequests(totalRequests.get())
                .successRequests(successRequests.get())
                .errorRequests(errorRequests.get())
                .currentRps(round2(rps))
                .avgLatency(round2(avgLat))
                .p95Latency(round2(p95))
                .p99Latency(round2(p99))
                .history(tail)
                .build();
    }

    // ======================== History ========================

    public List<PerformanceHistoryMeta> getHistoryList() {
        Path dir = Paths.get(HISTORY_DIR);
        if (!Files.exists(dir)) {
            return List.of();
        }
        List<PerformanceHistoryMeta> results = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
            for (Path entry : stream) {
                Path metaPath = entry.resolve("meta.json");
                if (Files.exists(metaPath)) {
                    try {
                        String json = Files.readString(metaPath);
                        PerformanceHistoryMeta meta = objectMapper.readValue(json, PerformanceHistoryMeta.class);
                        results.add(meta);
                    } catch (Exception e) {
                        log.warn("Failed to read history meta: {}", metaPath, e);
                    }
                }
            }
        } catch (IOException e) {
            log.warn("Failed to list history directory", e);
        }
        results.sort((a, b) -> b.getStartTime().compareTo(a.getStartTime()));
        return results;
    }

    public PerformanceHistoryDetail getHistoryDetail(String historyTestId) {
        Path testDir = Paths.get(HISTORY_DIR, historyTestId);
        if (!Files.exists(testDir)) {
            return null;
        }
        try {
            Map<String, Object> metaMap = readJsonMap(testDir.resolve("meta.json"));
            Map<String, Object> configMap = readJsonMap(testDir.resolve("config.json"));
            Map<String, Object> statsMap = readJsonMap(testDir.resolve("stats.json"));
            List<Map<String, Object>> historyList = readJsonList(testDir.resolve("history.json"));

            PerformanceHistoryMeta meta = objectMapper.convertValue(metaMap, PerformanceHistoryMeta.class);

            PerformanceAnalysis analysis = null;
            Path analysisPath = testDir.resolve("analysis.json");
            if (Files.exists(analysisPath)) {
                String json = Files.readString(analysisPath);
                analysis = objectMapper.readValue(json, PerformanceAnalysis.class);
            }

            return PerformanceHistoryDetail.builder()
                    .meta(meta)
                    .config(configMap)
                    .stats(statsMap)
                    .history(historyList)
                    .analysis(analysis)
                    .build();
        } catch (Exception e) {
            log.error("Error loading history detail for {}", historyTestId, e);
            return null;
        }
    }

    public void deleteHistory(String historyTestId) {
        Path testDir = Paths.get(HISTORY_DIR, historyTestId);
        if (Files.exists(testDir)) {
            try {
                try (DirectoryStream<Path> stream = Files.newDirectoryStream(testDir)) {
                    for (Path file : stream) {
                        Files.deleteIfExists(file);
                    }
                }
                Files.deleteIfExists(testDir);
            } catch (IOException e) {
                log.warn("Failed to delete history {}", historyTestId, e);
            }
        }
    }

    // ======================== Internal: Test Runners ========================

    private void runFatigue(int concurrency, int durationSec) {
        currentUsers = concurrency;
        CountDownLatch latch = new CountDownLatch(concurrency);
        for (int i = 0; i < concurrency; i++) {
            executor.submit(() -> {
                try {
                    workerLoop();
                } finally {
                    latch.countDown();
                }
            });
        }

        long endAt = System.currentTimeMillis() + durationSec * 1000L;
        while (System.currentTimeMillis() < endAt && !shouldStop.get()) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        shouldStop.set(true);
        try {
            latch.await(30, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private void runStep(int initial, int step, int stepDurationSec, int maxUsers) {
        List<Integer> stages = new ArrayList<>();
        for (int target = initial; target <= maxUsers; target += step) {
            stages.add(target);
        }

        AtomicInteger currentWorkerCount = new AtomicInteger(0);
        List<Future<?>> futures = new ArrayList<>();

        for (int stageTarget : stages) {
            if (shouldStop.get()) break;

            int usersToAdd = stageTarget - currentWorkerCount.get();
            long stageStart = System.currentTimeMillis();

            // Phase 1: Ramp-up (20% of duration)
            if (usersToAdd > 0) {
                long rampupMs = (long) (stepDurationSec * 1000L * 0.2);
                long interval = rampupMs / usersToAdd;

                for (int i = 0; i < usersToAdd; i++) {
                    if (shouldStop.get()) break;
                    futures.add(executor.submit(this::workerLoop));
                    currentWorkerCount.incrementAndGet();
                    currentUsers = currentWorkerCount.get();

                    long nextTime = stageStart + (long) (i + 1) * interval;
                    long wait = nextTime - System.currentTimeMillis();
                    if (wait > 0) {
                        try {
                            Thread.sleep(wait);
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                    }
                }
            }

            // Phase 2: Plateau (remaining duration)
            long plateauEnd = stageStart + stepDurationSec * 1000L;
            while (System.currentTimeMillis() < plateauEnd && !shouldStop.get()) {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }

        shouldStop.set(true);
        for (Future<?> f : futures) {
            try {
                f.get(30, TimeUnit.SECONDS);
            } catch (Exception ignored) {
                // workers should exit on shouldStop
            }
        }
    }

    private void workerLoop() {
        RestClient workerClient = RestClient.create();
        while (!shouldStop.get()) {
            Map<String, Object> payload = buildPayload(targetConfig);
            long start = System.currentTimeMillis();
            try {
                String body = workerClient.post()
                        .uri(GUARDRAIL_SERVICE_URL)
                        .header("Content-Type", "application/json")
                        .body(payload)
                        .retrieve()
                        .onStatus(HttpStatusCode::isError, (req, resp) -> {
                            // handled below via status check
                        })
                        .body(String.class);

                long durationMs = System.currentTimeMillis() - start;
                totalRequests.incrementAndGet();
                windowRequests.incrementAndGet();

                // Consider non-null body as success (guardrail returned something)
                if (body != null) {
                    successRequests.incrementAndGet();
                    latencySumMs.addAndGet(durationMs);
                    latencyCount.incrementAndGet();
                    windowLatencies.add((double) durationMs);
                } else {
                    errorRequests.incrementAndGet();
                    windowErrors.incrementAndGet();
                }
            } catch (Exception e) {
                totalRequests.incrementAndGet();
                windowRequests.incrementAndGet();
                errorRequests.incrementAndGet();
                windowErrors.incrementAndGet();
            }

            try {
                Thread.sleep(10); // small pause between requests
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    // ======================== Internal: Helpers ========================

    private Map<String, Object> buildPayload(GuardrailConfig config) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("request_id", UUID.randomUUID().toString());
        payload.put("app_id", config.getAppId());
        payload.put("apikey", "perf-test-" + UUID.randomUUID().toString().substring(0, 8));
        payload.put("input_prompt", config.getInputPrompt());
        payload.put("use_customize_white", config.isUseCustomizeWhite());
        payload.put("use_customize_words", config.isUseCustomizeWords());
        payload.put("use_customize_rule", config.isUseCustomizeRule());
        payload.put("use_vip_black", config.isUseVipBlack());
        payload.put("use_vip_white", config.isUseVipWhite());
        return payload;
    }

    private void resetStats() {
        totalRequests.set(0);
        successRequests.set(0);
        errorRequests.set(0);
        latencySumMs.set(0);
        latencyCount.set(0);
        windowRequests.set(0);
        windowErrors.set(0);
        windowStartMs = System.currentTimeMillis();
        windowLatencies.clear();
        historyBuffer.clear();
        lastRps = 0.0;
        lastErrorRps = 0.0;
        lastP95 = 0.0;
        lastP99 = 0.0;
    }

    private void snapshotHistory(long timestampMs, double rps, double errorRps, double p95, double p99) {
        double avgLat = 0.0;
        if (latencyCount.get() > 0) {
            avgLat = (double) latencySumMs.get() / latencyCount.get();
        }
        Map<String, Object> point = new LinkedHashMap<>();
        point.put("timestamp", timestampMs / 1000);
        point.put("rps", round2(rps));
        point.put("error_rps", round2(errorRps));
        point.put("latency", round2(avgLat));
        point.put("p95_latency", round2(p95));
        point.put("p99_latency", round2(p99));
        point.put("users", currentUsers);
        historyBuffer.add(point);
    }

    private void saveHistory() {
        if (testId == null || targetConfig == null) return;

        Path testDir = Paths.get(HISTORY_DIR, testId);
        try {
            Files.createDirectories(testDir);

            long endTs = endTimeMs > 0 ? endTimeMs : System.currentTimeMillis();
            int duration = (int) ((endTs - startTimeMs) / 1000);

            // meta.json
            Map<String, Object> meta = new LinkedHashMap<>();
            meta.put("test_id", testId);
            meta.put("start_time", formatTimestamp(startTimeMs));
            meta.put("end_time", formatTimestamp(endTs));
            meta.put("duration", duration);
            meta.put("test_type", testConfig != null ? testConfig.getTestType() : "UNKNOWN");
            meta.put("app_id", targetConfig.getAppId());
            meta.put("status", "COMPLETED");
            Files.writeString(testDir.resolve("meta.json"), objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(meta));

            // config.json
            if (testConfig != null) {
                Files.writeString(testDir.resolve("config.json"), objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(testConfig));
            }

            // stats.json
            double avgLatency = latencyCount.get() > 0 ? (double) latencySumMs.get() / latencyCount.get() : 0.0;
            double maxRps = historyBuffer.stream()
                    .mapToDouble(p -> ((Number) p.getOrDefault("rps", 0.0)).doubleValue())
                    .max().orElse(0.0);

            Map<String, Object> stats = new LinkedHashMap<>();
            stats.put("total_requests", totalRequests.get());
            stats.put("success_requests", successRequests.get());
            stats.put("error_requests", errorRequests.get());
            stats.put("avg_latency", round2(avgLatency));
            stats.put("max_rps", round2(maxRps));
            Files.writeString(testDir.resolve("stats.json"), objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(stats));

            // history.json
            Files.writeString(testDir.resolve("history.json"), objectMapper.writeValueAsString(historyBuffer));

            // analysis.json
            PerformanceAnalysis analysis = analyzeResults(stats, new ArrayList<>(historyBuffer));
            Files.writeString(testDir.resolve("analysis.json"), objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(analysis));

        } catch (IOException e) {
            log.error("Failed to save history for test {}", testId, e);
        }
    }

    private PerformanceAnalysis analyzeResults(Map<String, Object> stats, List<Map<String, Object>> history) {
        if (history.isEmpty()) {
            return PerformanceAnalysis.builder()
                    .score(0)
                    .conclusion("No valid test data collected.")
                    .suggestions(List.of("Please check network connectivity or service status."))
                    .build();
        }

        int maxUsersVal = history.stream().mapToInt(h -> ((Number) h.getOrDefault("users", 0)).intValue()).max().orElse(0);
        double maxRps = history.stream().mapToDouble(h -> ((Number) h.getOrDefault("rps", 0.0)).doubleValue()).max().orElse(0.0);

        List<Double> p99Values = history.stream()
                .map(h -> ((Number) h.getOrDefault("p99_latency", 0.0)).doubleValue())
                .toList();
        double maxP99 = p99Values.stream().mapToDouble(Double::doubleValue).max().orElse(0.0);
        double avgP99 = p99Values.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);

        long totalReqs = ((Number) stats.getOrDefault("total_requests", 0L)).longValue();
        long errorReqs = ((Number) stats.getOrDefault("error_requests", 0L)).longValue();
        double errorRate = totalReqs > 0 ? (errorReqs * 100.0 / totalReqs) : 0;

        int score = 100;
        List<String> suggestions = new ArrayList<>();

        if (errorRate > 1.0) {
            score -= 40;
            suggestions.add(String.format("High error rate: %.2f%% of requests failed. Check server logs.", errorRate));
        } else if (errorRate > 0) {
            score -= 10;
            suggestions.add(String.format("Minor errors: %.2f%% failure rate observed.", errorRate));
        }

        if (maxP99 > 2000) {
            score -= 30;
            suggestions.add(String.format("Severe latency: P99 peak reached %.0fms, exceeding 2s threshold.", maxP99));
        } else if (maxP99 > 1000) {
            score -= 10;
            suggestions.add(String.format("High latency: P99 peak reached %.0fms, exceeding 1s.", maxP99));
        }

        // Spike detection
        int spikeCount = 0;
        for (double v : p99Values) {
            if (v > Math.max(avgP99 * 2, 50)) spikeCount++;
        }
        if (spikeCount > 0) {
            score -= 5 * Math.min(spikeCount, 4);
            suggestions.add(String.format("Latency spikes detected: %d significant latency surges observed.", spikeCount));
        }

        if (score == 100) {
            suggestions.add("Perfect performance: System is extremely stable under current test load.");
        } else if (score >= 90) {
            suggestions.add("Excellent performance: System is generally stable with acceptable metrics.");
        }

        String conclusion = String.format(
                "Test simulated peak %d virtual users. Max throughput: %.1f RPS. P99 peak: %.1f ms, avg P99: %.1f ms. Total requests: %d, failures: %d.",
                maxUsersVal, maxRps, maxP99, avgP99, totalReqs, errorReqs);

        return PerformanceAnalysis.builder()
                .score(Math.max(0, score))
                .conclusion(conclusion)
                .suggestions(suggestions)
                .build();
    }

    // ======================== Utility ========================

    private static double percentile(List<Double> sorted, double pct) {
        if (sorted.isEmpty()) return 0.0;
        int idx = (int) (pct * sorted.size());
        if (idx >= sorted.size()) idx = sorted.size() - 1;
        return sorted.get(idx);
    }

    private static double round2(double val) {
        return Math.round(val * 100.0) / 100.0;
    }

    private String formatTimestamp(long ms) {
        return LocalDateTime.ofInstant(Instant.ofEpochMilli(ms), ZoneId.systemDefault()).format(ISO_FMT);
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> readJsonMap(Path path) throws IOException {
        String json = Files.readString(path);
        return objectMapper.readValue(json, new TypeReference<Map<String, Object>>() {});
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> readJsonList(Path path) throws IOException {
        String json = Files.readString(path);
        return objectMapper.readValue(json, new TypeReference<List<Map<String, Object>>>() {});
    }
}

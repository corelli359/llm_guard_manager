import React, { useState, useEffect, useRef } from 'react';
import { Card, Form, Input, Select, Switch, Button, Row, Col, Tabs, Statistic, message, Divider, Tag, Space, Drawer, Table, Popconfirm, Descriptions, Spin, Alert } from 'antd';
import { PlayCircleOutlined, StopOutlined, ThunderboltOutlined, CheckCircleOutlined, ClockCircleOutlined, HistoryOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { scenariosApi, performanceApi, getErrorMessage } from '../api';
import { ScenarioApp } from '../types';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { TabPane } = Tabs;

const PerformanceTestPage: React.FC = () => {
  const [form] = Form.useForm();
  const [apps, setApps] = useState<ScenarioApp[]>([]);
  const [loadingApps, setLoadingApps] = useState(false);
  
  // Test State
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState<any>(null);
  const [dryRunPassed, setDryRunPassed] = useState(false);
  
  // History State
  const [historyVisible, setHistoryVisible] = useState(false);
  const [historyList, setHistoryList] = useState<any[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Timer for polling
  const pollTimer = useRef<number | null>(null);

  useEffect(() => {
    fetchApps();
    // Check initial status in case page refreshed
    checkStatus();
    return () => stopPolling();
  }, []);

  const fetchApps = async () => {
    setLoadingApps(true);
    try {
      const res = await scenariosApi.getAll();
      setApps(res.data);
    } catch (error: any) {
      message.error(getErrorMessage(error, '加载应用列表失败'));
    } finally {
      setLoadingApps(false);
    }
  };

  const startPolling = () => {
    stopPolling();
    pollTimer.current = window.setInterval(checkStatus, 1000);
  };

  const stopPolling = () => {
    if (pollTimer.current) {
      clearInterval(pollTimer.current);
      pollTimer.current = null;
    }
  };

  const checkStatus = async () => {
    try {
      const res = await performanceApi.getStatus();
      const data = res.data;
      setStatus(data);
      setIsRunning(data.is_running);
      
      if (!data.is_running && pollTimer.current) {
         stopPolling();
         // Fetch one last time to ensure we have the final data including the 'stop' snapshot
         // But we are already processing 'res', which is the latest status.
         // Just ensure local state reflects stopped.
      }
    } catch (error) {
      console.error("Failed to fetch status", error);
    }
  };

  const handleDryRun = async () => {
    try {
      const values = await form.validateFields();
      // Extract only target config
      const targetConfig = {
          app_id: values.app_id,
          input_prompt: values.input_prompt,
          use_customize_white: values.use_customize_white,
          use_customize_words: values.use_customize_words,
          use_customize_rule: values.use_customize_rule,
          use_vip_black: values.use_vip_black,
          use_vip_white: values.use_vip_white
      };

      message.loading({ content: '正在执行连通性测试...', key: 'dryRun' });
      const res = await performanceApi.dryRun(targetConfig);
      
      if (res.data.success) {
          message.success({ content: `测试通过! 耗时: ${res.data.latency}ms`, key: 'dryRun' });
          setDryRunPassed(true);
      } else {
          message.error({ content: `测试失败: ${res.data.error}`, key: 'dryRun' });
          setDryRunPassed(false);
      }
    } catch (error) {
        message.error({ content: '验证失败，请检查表单', key: 'dryRun' });
    }
  };

  const handleStart = async () => {
    try {
        const values = await form.validateFields();
        const targetConfig = {
            app_id: values.app_id,
            input_prompt: values.input_prompt,
            use_customize_white: values.use_customize_white,
            use_customize_words: values.use_customize_words,
            use_customize_rule: values.use_customize_rule,
            use_vip_black: values.use_vip_black,
            use_vip_white: values.use_vip_white
        };

        let stepConfig = null;
        let fatigueConfig = null;
        const testType = values.test_type; // 'STEP' or 'FATIGUE'

        if (testType === 'STEP') {
            stepConfig = {
                initial_users: parseInt(values.step_initial_users),
                step_size: parseInt(values.step_size),
                step_duration: parseInt(values.step_duration),
                max_users: parseInt(values.step_max_users)
            };
        } else {
            fatigueConfig = {
                concurrency: parseInt(values.fatigue_concurrency),
                duration: parseInt(values.fatigue_duration)
            };
        }

        await performanceApi.start({
            test_type: testType,
            target_config: targetConfig,
            step_config: stepConfig,
            fatigue_config: fatigueConfig
        });

        message.success('压测任务已启动');
        setIsRunning(true);
        startPolling();

    } catch (error: any) {
        message.error(getErrorMessage(error, '启动失败'));
    }
  };

  const handleStop = async () => {
      try {
          await performanceApi.stop();
          message.warning('正在停止...');
      } catch (e: any) {
          message.error(getErrorMessage(e, '停止失败'));
      }
  };
  
  const fetchHistory = async () => {
      setHistoryLoading(true);
      try {
          const res = await performanceApi.getHistoryList();
          setHistoryList(res.data);
      } catch (e: any) {
          message.error(getErrorMessage(e, '获取历史记录失败'));
      } finally {
          setHistoryLoading(false);
      }
  };

  const openHistory = () => {
      setHistoryVisible(true);
      fetchHistory();
  };

  const handleViewDetail = async (record: any) => {
      setDetailVisible(true);
      setDetailLoading(true);
      try {
          const res = await performanceApi.getHistoryDetail(record.test_id);
          setSelectedHistory(res.data);
      } catch (e: any) {
          message.error(getErrorMessage(e, '加载详情失败'));
      } finally {
          setDetailLoading(false);
      }
  };

  const handleDeleteHistory = async (testId: string) => {
      try {
          await performanceApi.deleteHistory(testId);
          message.success('记录已删除');
          fetchHistory();
      } catch (e: any) {
          message.error(getErrorMessage(e, '删除失败'));
      }
  };

  // Helper to format history for chart
  const chartData = status?.history || [];

  return (
    <div style={{ padding: '0 24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <h2>性能与疲劳测试</h2>
          <Button icon={<HistoryOutlined />} onClick={openHistory}>历史记录</Button>
      </div>
      
      <Row gutter={24}>
        {/* Left Config Panel */}
        <Col span={10}>
          <Card title="测试配置" bordered={false}>
            <Form form={form} layout="vertical" initialValues={{
                use_customize_white: false,
                use_customize_words: true,
                use_customize_rule: true,
                use_vip_black: false,
                use_vip_white: false,
                test_type: 'STEP',
                step_initial_users: 1,
                step_size: 5,
                step_duration: 10,
                step_max_users: 50,
                fatigue_concurrency: 20,
                fatigue_duration: 60
            }}>
                <Divider orientation="left">目标 (Target)</Divider>
                <Form.Item name="app_id" label="选择场景 (App ID)" rules={[{ required: true }]}>
                    <Select placeholder="选择应用" loading={loadingApps} showSearch disabled={isRunning}>
                        {apps.map(app => <Select.Option key={app.app_id} value={app.app_id}>{app.app_name} ({app.app_id})</Select.Option>)}
                    </Select>
                </Form.Item>
                <Form.Item name="input_prompt" label="测试 Prompt" rules={[{ required: true }]}>
                    <TextArea rows={3} placeholder="输入用于测试的文本..." disabled={isRunning} />
                </Form.Item>
                <Row gutter={16}>
                    <Col span={12}><Form.Item name="use_customize_white" label="自定义白名单" valuePropName="checked"><Switch size="small" disabled={isRunning}/></Form.Item></Col>
                    <Col span={12}><Form.Item name="use_vip_black" label="VIP 黑名单" valuePropName="checked"><Switch size="small" disabled={isRunning}/></Form.Item></Col>
                    <Col span={12}><Form.Item name="use_customize_words" label="自定义敏感词" valuePropName="checked"><Switch size="small" disabled={isRunning}/></Form.Item></Col>
                    <Col span={12}><Form.Item name="use_vip_white" label="VIP 白名单" valuePropName="checked"><Switch size="small" disabled={isRunning}/></Form.Item></Col>
                </Row>

                <Button type="dashed" block onClick={handleDryRun} icon={<ThunderboltOutlined />} disabled={isRunning} style={{ marginBottom: 24 }}>
                    连通性测试 (Dry Run)
                </Button>

                <Divider orientation="left">策略 (Policy)</Divider>
                {dryRunPassed ? (
                   <>
                    <Form.Item name="test_type" label="测试模式">
                        <Tabs type="card" onChange={(val) => form.setFieldsValue({ test_type: val })}>
                            <TabPane tab="阶梯测试 (Step Load)" key="STEP" />
                            <TabPane tab="疲劳测试 (Fatigue)" key="FATIGUE" />
                        </Tabs>
                    </Form.Item>
                    
                    <Form.Item noStyle shouldUpdate={(prev, curr) => prev.test_type !== curr.test_type}>
                        {({ getFieldValue }) => {
                            return getFieldValue('test_type') === 'STEP' ? (
                                <Row gutter={16}>
                                    <Col span={12}><Form.Item name="step_initial_users" label="初始并发"><Input type="number" disabled={isRunning}/></Form.Item></Col>
                                    <Col span={12}><Form.Item name="step_max_users" label="最大并发"><Input type="number" disabled={isRunning}/></Form.Item></Col>
                                    <Col span={12}><Form.Item name="step_size" label="步长 (增加用户/轮)"><Input type="number" disabled={isRunning}/></Form.Item></Col>
                                    <Col span={12}><Form.Item name="step_duration" label="步长间隔 (秒)"><Input type="number" disabled={isRunning}/></Form.Item></Col>
                                </Row>
                            ) : (
                                <Row gutter={16}>
                                    <Col span={12}><Form.Item name="fatigue_concurrency" label="并发数 (Users)"><Input type="number" disabled={isRunning}/></Form.Item></Col>
                                    <Col span={12}><Form.Item name="fatigue_duration" label="持续时间 (秒)"><Input type="number" disabled={isRunning}/></Form.Item></Col>
                                </Row>
                            );
                        }}
                    </Form.Item>

                    <Button 
                        type="primary" 
                        danger={isRunning} 
                        icon={isRunning ? <StopOutlined /> : <PlayCircleOutlined />} 
                        block 
                        size="large"
                        onClick={isRunning ? handleStop : handleStart}
                    >
                        {isRunning ? '停止测试' : '开始测试'}
                    </Button>
                   </>
                ) : (
                    <div style={{ textAlign: 'center', color: '#999' }}>
                        <StopOutlined style={{ fontSize: 24, marginBottom: 8 }} />
                        <p>请先通过连通性测试以解锁压测配置</p>
                    </div>
                )}
            </Form>
          </Card>
        </Col>

        {/* Right Monitor Panel */}
        <Col span={14}>
            <Card title={
                <Space>
                    <span>实时监控</span>
                    {isRunning && <Tag color="processing" icon={<ClockCircleOutlined />}>Running</Tag>}
                    {!isRunning && status?.total_requests > 0 && <Tag color="default">Stopped</Tag>}
                </Space>
            } bordered={false}>
                <Row gutter={16} style={{ marginBottom: 24 }}>
                    <Col span={4}>
                        <Statistic title="运行时长 (s)" value={status?.duration || 0} />
                    </Col>
                    <Col span={4}>
                        <Statistic title="当前虚拟用户数" value={status?.current_users || 0} valueStyle={{ color: '#1890ff' }} />
                    </Col>
                    <Col span={4}>
                        <Statistic title="实时 RPS (TPS)" value={status?.current_rps || 0} precision={1} />
                    </Col>
                    <Col span={4}>
                        <Statistic title="Avg 响应时间 (ms)" value={status?.avg_latency || 0} precision={1} valueStyle={{ color: (status?.avg_latency || 0) > 1000 ? '#cf1322' : '#3f8600' }} />
                    </Col>
                    <Col span={4}>
                        <Statistic title="P95 响应时间 (ms)" value={status?.p95_latency || 0} precision={1} valueStyle={{ color: '#faad14' }} />
                    </Col>
                    <Col span={4}>
                        <Statistic title="P99 响应时间 (ms)" value={status?.p99_latency || 0} precision={1} valueStyle={{ color: '#cf1322' }} />
                    </Col>
                </Row>
                <Row gutter={16} style={{ marginBottom: 24 }}>
                   <Col span={8}>
                        <Statistic title="总请求量" value={status?.total_requests || 0} />
                   </Col>
                   <Col span={8}>
                        <Statistic title="成功请求数" value={status?.success_requests || 0} valueStyle={{ color: '#3f8600' }} prefix={<CheckCircleOutlined />} />
                   </Col>
                   <Col span={8}>
                        <Statistic title="失败请求数" value={status?.error_requests || 0} valueStyle={{ color: '#cf1322' }} />
                   </Col>
                </Row>

                <Divider />
                
                {/* Row 1: Response Time */}
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Card size="small" title="响应时间 (Response Time)" bordered={false}>
                            <div style={{ height: 200 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="timestamp" tick={false} />
                                        <YAxis unit="ms" />
                                        <Tooltip labelFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                                        <Legend />
                                        <Line type="monotone" dataKey="latency" stroke="#82ca9d" name="Avg 响应时间" isAnimationActive={false} dot={false} strokeWidth={2} />
                                        <Line type="monotone" dataKey="p95_latency" stroke="#faad14" name="P95 响应时间" isAnimationActive={false} dot={false} strokeDasharray="5 5" />
                                        <Line type="monotone" dataKey="p99_latency" stroke="#cf1322" name="P99 响应时间" isAnimationActive={false} dot={false} strokeDasharray="3 3" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </Card>
                    </Col>
                </Row>

                {/* Row 2: Throughput Breakdown */}
                <Row gutter={[16, 16]}>
                    <Col span={12}>
                        <Card size="small" title="总吞吐量 (Total Throughput)" bordered={false}>
                            <div style={{ height: 200 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="timestamp" tick={false} />
                                        <YAxis />
                                        <Tooltip labelFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                                        <Legend />
                                        <Line type="monotone" dataKey="rps" stroke="#8884d8" name="总吞吐量 (RPS)" isAnimationActive={false} dot={false} strokeWidth={2} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </Card>
                    </Col>
                    <Col span={12}>
                        <Card size="small" title="吞吐量细分 (Throughput Breakdown)" bordered={false}>
                            <div style={{ height: 200 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="timestamp" tick={false} />
                                        <YAxis />
                                        <Tooltip labelFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                                        <Legend />
                                        <Line type="monotone" dataKey="rps" stroke="#3f8600" name="成功吞吐量" isAnimationActive={false} dot={false} strokeWidth={2} />
                                        <Line type="monotone" dataKey="error_rps" stroke="#cf1322" name="失败吞吐量" isAnimationActive={false} dot={false} strokeWidth={2} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </Card>
                    </Col>
                </Row>

                {/* Row 3: VUsers & Errors */}
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Card size="small" title="虚拟用户数 (Virtual Users)" bordered={false}>
                            <div style={{ height: 200 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="timestamp" tick={false} />
                                        <YAxis />
                                        <Tooltip labelFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                                        <Legend />
                                        <Line type="step" dataKey="users" stroke="#ff7300" name="虚拟用户数" isAnimationActive={false} dot={false} strokeWidth={2} fill="#ff7300" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </Card>
                    </Col>
                </Row>
            </Card>
        </Col>
      </Row>

      {/* History List Drawer */}
      <Drawer
        title="测试历史记录"
        placement="right"
        onClose={() => setHistoryVisible(false)}
        open={historyVisible}
        width={600}
      >
        <Table
            dataSource={historyList}
            rowKey="test_id"
            loading={historyLoading}
            columns={[
                { title: '时间', dataIndex: 'start_time', key: 'start_time', render: t => dayjs(t).format('MM-DD HH:mm') },
                { title: '应用', dataIndex: 'app_id', key: 'app_id' },
                { title: '类型', dataIndex: 'test_type', key: 'test_type', render: t => <Tag>{t}</Tag> },
                { title: '耗时(s)', dataIndex: 'duration', key: 'duration' },
                { title: '状态', dataIndex: 'status', key: 'status', render: t => <Tag color={t==='COMPLETED'?'green':'default'}>{t}</Tag> },
                {
                    title: '操作',
                    key: 'action',
                    render: (_, record) => (
                        <Space>
                            <Button icon={<EyeOutlined />} size="small" onClick={() => handleViewDetail(record)} />
                            <Popconfirm title="确定删除?" onConfirm={() => handleDeleteHistory(record.test_id)}>
                                <Button icon={<DeleteOutlined />} size="small" danger />
                            </Popconfirm>
                        </Space>
                    )
                }
            ]}
        />
      </Drawer>

      {/* History Detail Drawer */}
      <Drawer
        title="测试详情回顾"
        placement="right"
        onClose={() => setDetailVisible(false)}
        open={detailVisible}
        width={800}
      >
        {detailLoading ? <Spin /> : selectedHistory && (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
                {/* Analysis Report Section */}
                {selectedHistory.analysis && (
                    <Card title="智能分析报告" bordered={false} className="analysis-card">
                        <Alert
                            message={`综合评分: ${selectedHistory.analysis.score} 分`}
                            description={selectedHistory.analysis.conclusion}
                            type={selectedHistory.analysis.score >= 80 ? 'success' : (selectedHistory.analysis.score >= 60 ? 'warning' : 'error')}
                            showIcon
                            style={{ marginBottom: 16 }}
                        />
                        {selectedHistory.analysis.suggestions.length > 0 && (
                            <div style={{ marginTop: 12 }}>
                                <h4>优化建议:</h4>
                                <ul>
                                    {selectedHistory.analysis.suggestions.map((s: string, i: number) => (
                                        <li key={i}>{s}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </Card>
                )}

                <Descriptions title="基础信息" bordered column={2}>
                    <Descriptions.Item label="Test ID">{selectedHistory.meta.test_id}</Descriptions.Item>
                    <Descriptions.Item label="App ID">{selectedHistory.meta.app_id}</Descriptions.Item>
                    <Descriptions.Item label="Start Time">{dayjs(selectedHistory.meta.start_time).format('YYYY-MM-DD HH:mm:ss')}</Descriptions.Item>
                    <Descriptions.Item label="Duration">{selectedHistory.meta.duration} s</Descriptions.Item>
                    <Descriptions.Item label="Total Requests">{selectedHistory.stats.total_requests}</Descriptions.Item>
                    <Descriptions.Item label="Max RPS">{selectedHistory.stats.max_rps}</Descriptions.Item>
                    <Descriptions.Item label="Avg Latency">{selectedHistory.stats.avg_latency} ms</Descriptions.Item>
                    <Descriptions.Item label="P95 Latency">{selectedHistory.history[selectedHistory.history.length-1]?.p95_latency || '-'} ms</Descriptions.Item>
                    <Descriptions.Item label="P99 Latency">{selectedHistory.history[selectedHistory.history.length-1]?.p99_latency || '-'} ms</Descriptions.Item>
                    <Descriptions.Item label="Error Rate">{selectedHistory.stats.total_requests > 0 ? (selectedHistory.stats.error_requests / selectedHistory.stats.total_requests * 100).toFixed(2) : 0}%</Descriptions.Item>
                </Descriptions>
                
                <Card title="RPS 趋势回放" bordered={false}>
                    <div style={{ height: 250 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={selectedHistory.history}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="timestamp" tick={false} />
                                <YAxis />
                                <Tooltip labelFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                                <Legend />
                                <Line type="monotone" dataKey="rps" stroke="#8884d8" name="Total RPS" isAnimationActive={false} dot={false} strokeWidth={2} />
                                <Line type="monotone" dataKey="error_rps" stroke="#ff4d4f" name="Error RPS" isAnimationActive={false} dot={false} strokeDasharray="5 5" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card title="延迟趋势回放" bordered={false}>
                    <div style={{ height: 250 }}>
                         <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={selectedHistory.history}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="timestamp" tick={false} />
                                <YAxis yAxisId="left" unit="ms" />
                                <YAxis yAxisId="right" orientation="right" />
                                <Tooltip labelFormatter={(t) => new Date(t*1000).toLocaleTimeString()} />
                                <Legend />
                                <Line yAxisId="left" type="monotone" dataKey="latency" stroke="#82ca9d" name="Avg Latency" isAnimationActive={false} dot={false} />
                                <Line yAxisId="left" type="monotone" dataKey="p95_latency" stroke="#faad14" name="P95 Latency" isAnimationActive={false} dot={false} strokeDasharray="5 5" />
                                <Line yAxisId="left" type="monotone" dataKey="p99_latency" stroke="#cf1322" name="P99 Latency" isAnimationActive={false} dot={false} strokeDasharray="3 3" />
                                <Line yAxisId="right" type="step" dataKey="users" stroke="#ff7300" name="Users" isAnimationActive={false} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
                
                <Card title="详细配置" size="small">
                    <pre style={{ maxHeight: 200, overflow: 'auto', background: '#f5f5f5', padding: 8 }}>
                        {JSON.stringify(selectedHistory.config, null, 2)}
                    </pre>
                </Card>
            </Space>
        )}
      </Drawer>
    </div>
  );
};

export default PerformanceTestPage;

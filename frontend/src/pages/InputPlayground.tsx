import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Select, Switch, Button, Row, Col, Typography, Tag, Divider, Space, message, Spin, Drawer, List, Tooltip, Modal, Descriptions } from 'antd';
import { PlayCircleOutlined, BugOutlined, CheckCircleOutlined, StopOutlined, EditOutlined, UserOutlined, HistoryOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import { scenariosApi, playgroundApi } from '../api';
import { ScenarioApp, PlaygroundResponse, PlaygroundHistory } from '../types';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const InputPlayground: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioApp[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetchingScenarios, setFetchingScenarios] = useState(false);
  const [result, setResult] = useState<PlaygroundResponse | null>(null);
  const [form] = Form.useForm();

  // History State
  const [historyVisible, setHistoryVisible] = useState(false);
  const [historyList, setHistoryList] = useState<PlaygroundHistory[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  
  // History Detail Modal State
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState<PlaygroundHistory | null>(null);

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    setFetchingScenarios(true);
    try {
      const res = await scenariosApi.getAll();
      setScenarios(res.data);
    } catch (error) {
      message.error('获取场景列表失败');
    } finally {
      setFetchingScenarios(false);
    }
  };

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await playgroundApi.getHistory({
        playground_type: 'INPUT',
        size: 50
      });
      setHistoryList(res.data);
    } catch (error) {
      message.error('获取历史记录失败');
    } finally {
      setHistoryLoading(false);
    }
  };

  const openHistory = () => {
    setHistoryVisible(true);
    fetchHistory();
  };

  const handleRestore = (item: PlaygroundHistory) => {
    // Restore form values
    const config = item.config_snapshot || {};
    form.setFieldsValue({
      app_id: item.app_id,
      input_prompt: item.input_data.input_prompt,
      use_customize_white: config.use_customize_white ?? false,
      use_customize_words: config.use_customize_words ?? false,
      use_customize_rule: config.use_customize_rule ?? false,
      use_vip_black: config.use_vip_black ?? false,
      use_vip_white: config.use_vip_white ?? false,
    });
    
    // Restore result view if output_data exists
    if (item.output_data) {
       setResult(item.output_data);
    }
    
    message.success('已恢复历史配置');
    setHistoryVisible(false);
  };
  
  const handleViewDetails = (item: PlaygroundHistory) => {
      setSelectedHistory(item);
      setDetailVisible(true);
  };

  const handleRun = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      setResult(null);
      const res = await playgroundApi.testInput(values);
      setResult(res.data);
      message.success('检测完成');
    } catch (error: any) {
      console.error(error);
      if (error.response && error.response.data && error.response.data.detail) {
        message.error(`检测失败: ${error.response.data.detail}`);
      } else {
        message.error('检测请求失败，请检查后端服务');
      }
    } finally {
      setLoading(false);
    }
  };

  const getDecisionUI = (score: number | undefined) => {
    if (score === undefined) return null;

    if (score === -1) {
        return (
          <Card style={{ borderLeft: '8px solid #ff4d4f', backgroundColor: '#fff2f0' }}>
            <Space direction="vertical">
              <Title level={4} style={{ color: '#ff4d4f', margin: 0 }}>
                <StopOutlined /> 错误 (Error)
              </Title>
              <Text>请求执行失败，请检查输出详情。</Text>
              <Tag color="red">Score: {score}</Tag>
            </Space>
          </Card>
        );
    }

    if (score === 0) {
      return (
        <Card style={{ borderLeft: '8px solid #52c41a', backgroundColor: '#f6ffed' }}>
          <Space direction="vertical">
            <Title level={4} style={{ color: '#52c41a', margin: 0 }}>
              <CheckCircleOutlined /> 通过 (Pass)
            </Title>
            <Text>内容安全，未命中有害规则。</Text>
            <Tag color="green">Score: {score}</Tag>
          </Space>
        </Card>
      );
    }
    if (score === 50) {
      return (
        <Card style={{ borderLeft: '8px solid #faad14', backgroundColor: '#fffbe6' }}>
          <Space direction="vertical">
            <Title level={4} style={{ color: '#faad14', margin: 0 }}>
              <EditOutlined /> 改写 (Rewrite)
            </Title>
            <Text>命中部分敏感词，建议脱敏或改写后发布。</Text>
            <Tag color="warning">Score: {score}</Tag>
          </Space>
        </Card>
      );
    }
    if (score === 100) {
      return (
        <Card style={{ borderLeft: '8px solid #f5222d', backgroundColor: '#fff1f0' }}>
          <Space direction="vertical">
            <Title level={4} style={{ color: '#f5222d', margin: 0 }}>
              <StopOutlined /> 拒答 (Block)
            </Title>
            <Text>命中高风险敏感词，内容已被拦截。</Text>
            <Tag color="error">Score: {score}</Tag>
          </Space>
        </Card>
      );
    }
    if (score === 1000) {
      return (
        <Card style={{ borderLeft: '8px solid #722ed1', backgroundColor: '#f9f0ff' }}>
          <Space direction="vertical">
            <Title level={4} style={{ color: '#722ed1', margin: 0 }}>
              <UserOutlined /> 转人工 (Manual)
            </Title>
            <Text>内容复杂或存在潜在风险，需人工审核。</Text>
            <Tag color="purple">Score: {score}</Tag>
          </Space>
        </Card>
      );
    }

    return (
      <Card>
        <Title level={4}>未知决策</Title>
        <Tag>Score: {score}</Tag>
      </Card>
    );
  };
  
  const getScoreTag = (score: number) => {
      if (score === -1) return <Tag color="red">Error</Tag>;
      if (score === 0) return <Tag color="green">Pass</Tag>;
      if (score === 50) return <Tag color="orange">Rewrite</Tag>;
      if (score === 100) return <Tag color="red">Block</Tag>;
      return <Tag>{score}</Tag>;
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>输入试验场 (Input Playground)</Title>
          <Paragraph style={{ margin: 0 }}>
            在这里您可以模拟用户输入，测试不同场景下的安全围栏检测效果。
          </Paragraph>
        </div>
        <Button 
          icon={<HistoryOutlined />} 
          onClick={openHistory}
        >
          历史记录
        </Button>
      </div>

      <Row gutter={24}>
        <Col span={10}>
          <Card title={<Space><BugOutlined /> 配置测试参数</Space>}>
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                use_customize_white: false,
                use_customize_words: true,
                use_customize_rule: true,
                use_vip_black: false,
                use_vip_white: false,
              }}
            >
              <Form.Item
                name="app_id"
                label="选择场景 (app_id)"
                rules={[{ required: true, message: '请选择一个场景' }]}
              >
                <Select
                  placeholder="搜索场景..."
                  loading={fetchingScenarios}
                  showSearch
                  optionFilterProp="children"
                >
                  {scenarios.map((s) => (
                    <Select.Option key={s.app_id} value={s.app_id}>
                      {s.app_name} ({s.app_id})
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="input_prompt"
                label="测试文本 (Input Prompt)"
                rules={[{ required: true, message: '请输入测试内容' }]}
              >
                <TextArea rows={6} placeholder="输入需要检测的内容..." />
              </Form.Item>

              <Divider orientation="left" plain>高级检测开关</Divider>
              
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Form.Item name="use_customize_white" label="自定义白名单" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="use_customize_words" label="自定义敏感词" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="use_customize_rule" label="自定义规则" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="use_vip_black" label="VIP 黑名单" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="use_vip_white" label="VIP 白名单" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item style={{ marginTop: 24 }}>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={handleRun}
                  loading={loading}
                  block
                  size="large"
                >
                  开始检测
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col span={14}>
          <Card title="检测结果" style={{ minHeight: 600 }}>
            {!result && !loading && (
              <div style={{ textAlign: 'center', padding: '100px 0', color: '#999' }}>
                <PlayCircleOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>配置参数并点击“开始检测”查看结果</p>
              </div>
            )}

            {loading && (
              <div style={{ textAlign: 'center', padding: '100px 0' }}>
                <Spin size="large" tip="正在请求围栏服务..." />
              </div>
            )}

            {result && (
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                {getDecisionUI(result.final_decision?.score)}

                <Divider orientation="left">决策详情 (all_decision_dict)</Divider>
                <pre style={{ 
                  backgroundColor: '#f5f5f5', 
                  padding: '16px', 
                  borderRadius: '4px',
                  maxHeight: '300px',
                  overflow: 'auto'
                }}>
                  {JSON.stringify(result.all_decision_dict, null, 2)}
                </pre>

                <Divider orientation="left">原始响应 (Raw Response)</Divider>
                <pre style={{ 
                  backgroundColor: '#f5f5f5', 
                  padding: '16px', 
                  borderRadius: '4px',
                  maxHeight: '300px',
                  overflow: 'auto'
                }}>
                  {JSON.stringify(result, null, 2)}
                </pre>
              </Space>
            )}
          </Card>
        </Col>
      </Row>

      <Drawer
        title="历史记录 (History)"
        placement="right"
        onClose={() => setHistoryVisible(false)}
        open={historyVisible}
        width={400}
      >
        <List
          loading={historyLoading}
          dataSource={historyList}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Tooltip title="查看详情">
                    <Button type="link" icon={<EyeOutlined />} onClick={() => handleViewDetails(item)} />
                </Tooltip>,
                <Tooltip title="回填配置并查看结果">
                  <Button type="link" icon={<ReloadOutlined />} onClick={() => handleRestore(item)} />
                </Tooltip>
              ]}
            >
              <List.Item.Meta
                title={
                    <Space>
                        {getScoreTag(item.score)}
                        <Text type="secondary" style={{ fontSize: 12 }}>
                            {dayjs(item.created_at).format('MM-DD HH:mm:ss')}
                        </Text>
                    </Space>
                }
                description={
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Tag>{item.app_id}</Tag>
                            {item.latency !== undefined && (
                                <Tooltip title={`总耗时: ${item.latency}ms / 上游: ${item.upstream_latency ?? '-'}ms`}>
                                    <Tag color="blue">{item.latency}ms</Tag>
                                </Tooltip>
                            )}
                        </div>
                        <div style={{ 
                            marginTop: 4, 
                            overflow: 'hidden', 
                            textOverflow: 'ellipsis', 
                            whiteSpace: 'nowrap', 
                            maxWidth: 250,
                            color: '#666'
                        }}>
                            {item.input_data.input_prompt}
                        </div>
                    </div>
                }
              />
            </List.Item>
          )}
        />
      </Drawer>
      
      <Modal
        title="历史详情 (History Details)"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={800}
      >
        {selectedHistory && (
            <Space direction="vertical" style={{ width: '100%' }}>
                <Descriptions bordered column={1}>
                    <Descriptions.Item label="Request ID">{selectedHistory.request_id}</Descriptions.Item>
                    <Descriptions.Item label="App ID">{selectedHistory.app_id}</Descriptions.Item>
                    <Descriptions.Item label="Time">{dayjs(selectedHistory.created_at).format('YYYY-MM-DD HH:mm:ss')}</Descriptions.Item>
                    <Descriptions.Item label="Score">{getScoreTag(selectedHistory.score)}</Descriptions.Item>
                    <Descriptions.Item label="Latency (Total)">
                        {selectedHistory.latency ? `${selectedHistory.latency} ms` : '-'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Latency (Upstream)">
                        {selectedHistory.upstream_latency ? `${selectedHistory.upstream_latency} ms` : '-'}
                    </Descriptions.Item>
                </Descriptions>
                
                <Title level={5}>Input Prompt</Title>
                <div style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', whiteSpace: 'pre-wrap' }}>
                    {selectedHistory.input_data.input_prompt}
                </div>

                <Title level={5}>Config Snapshot</Title>
                <pre style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', maxHeight: 200, overflow: 'auto' }}>
                    {JSON.stringify(selectedHistory.config_snapshot, null, 2)}
                </pre>
                
                <Title level={5}>Output Response</Title>
                <pre style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', maxHeight: 400, overflow: 'auto' }}>
                    {JSON.stringify(selectedHistory.output_data, null, 2)}
                </pre>
            </Space>
        )}
      </Modal>
    </div>
  );
};

export default InputPlayground;

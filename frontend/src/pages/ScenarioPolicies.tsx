import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Card, Row, Col, Tag, Radio } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { RuleScenarioPolicy, MetaTag } from '../types';
import { rulePoliciesApi, metaTagsApi } from '../api';

const ScenarioPoliciesPage: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const navigate = useNavigate();

  const [policies, setPolicies] = useState<RuleScenarioPolicy[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [currentScenarioId, setCurrentScenarioId] = useState<string>('');
  const [searchScenarioId, setSearchScenarioId] = useState<string>('');
  const [matchType, setMatchType] = useState<'KEYWORD' | 'TAG'>('KEYWORD');
  
  const [form] = Form.useForm();

  // Initial load from URL
  useEffect(() => {
    fetchTags();
    if (appId) {
        setCurrentScenarioId(appId);
        setSearchScenarioId(appId);
        fetchPolicies(appId);
    }
  }, [appId]);

  const fetchTags = async () => {
    try {
      const res = await metaTagsApi.getAll();
      setTags(res.data);
    } catch (error) {
      console.error('Failed to fetch tags', error);
    }
  };

  const fetchPolicies = async (scenarioId: string) => {
    if (!scenarioId) return;
    setLoading(true);
    try {
      const res = await rulePoliciesApi.getByScenario(scenarioId);
      setPolicies(res.data);
      setCurrentScenarioId(scenarioId);
    } catch (error) {
      message.error('获取策略列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchScenarioId.trim()) {
      fetchPolicies(searchScenarioId.trim());
    } else {
      message.warning('请输入场景 ID');
    }
  };


  const handleAdd = () => {
    if (!currentScenarioId) {
      message.warning('请先选择一个场景');
      return;
    }
    setEditingId(null);
    form.resetFields();
    setMatchType('KEYWORD'); // Reset local state
    form.setFieldsValue({ 
      scenario_id: currentScenarioId,
      is_active: true, 
      rule_mode: 1, // Default Custom
      match_type: 'KEYWORD',
      strategy: 'BLOCK'
    });
    setIsModalOpen(true);
  };

  const handleEdit = (record: RuleScenarioPolicy) => {
    setEditingId(record.id);
    setMatchType(record.match_type); // Sync local state
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await rulePoliciesApi.delete(id);
      message.success('策略已删除');
      if (currentScenarioId) fetchPolicies(currentScenarioId);
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await rulePoliciesApi.update(editingId, values);
        message.success('策略已更新');
      } else {
        await rulePoliciesApi.create(values);
        message.success('策略已创建');
      }
      setIsModalOpen(false);
      if (currentScenarioId) fetchPolicies(currentScenarioId);
    } catch (error: any) {
      console.error(error);
      if (error.response && error.response.data && error.response.data.detail) {
        message.error(`操作失败: ${error.response.data.detail}`);
      } else if (error.errorFields) {
         // Form validation error, do nothing
      } else {
        message.error('操作失败，请重试');
      }
    }
  };

  const handleMatchTypeChange = (e: any) => {
    setMatchType(e.target.value);
    // Optional: Clear dependent fields when switching type
    form.setFieldsValue({ match_value: '', extra_condition: '' });
  };

  const columns = [
    { title: '规则模式', dataIndex: 'rule_mode', key: 'rule_mode', 
      render: (val: number) => val === 0 ? <Tag color="gold">超级模式 (0)</Tag> : <Tag color="blue">自定义 (1)</Tag>
    },
    { title: '匹配类型', dataIndex: 'match_type', key: 'match_type',
      render: (val: string) => <Tag>{val === 'KEYWORD' ? '敏感词' : '标签'}</Tag>
    },
    { title: '匹配内容', dataIndex: 'match_value', key: 'match_value' },
    { title: '额外条件', dataIndex: 'extra_condition', key: 'extra_condition' },
    { title: '处置策略', dataIndex: 'strategy', key: 'strategy',
      render: (val: string) => {
        let color = 'default';
        let text = val;
        if (val === 'BLOCK') { color = 'red'; text = '拦截 (BLOCK)'; }
        if (val === 'PASS') { color = 'green'; text = '放行 (PASS)'; }
        if (val === 'REWRITE') { color = 'orange'; text = '重写 (REWRITE)'; }
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '是否启用',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: RuleScenarioPolicy) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定要删除此策略吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        {appId && (
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/apps/${appId}`)} style={{ marginBottom: 16 }}>
                返回应用概览
            </Button>
        )}
        <h2>场景策略管理 {appId ? `- ${appId}` : ''}</h2>
        {!appId && (
            <Card title="选择场景">
            <Row gutter={16} align="middle">
                <Col>
                <span>场景 ID (Scenario ID): </span>
                </Col>
                <Col flex="auto">
                <Input 
                    placeholder="请输入场景 ID" 
                    value={searchScenarioId}
                    onChange={e => setSearchScenarioId(e.target.value)}
                    onPressEnter={handleSearch}
                />
                </Col>
                <Col>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                    加载策略
                </Button>
                </Col>
            </Row>
            </Card>
        )}
      </div>

      {currentScenarioId && (
        <>
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增策略 ({currentScenarioId})
            </Button>
          </div>
          <Table 
            columns={columns} 
            dataSource={policies} 
            rowKey="id" 
            loading={loading}
          />
        </>
      )}

      <Modal 
        title={editingId ? "编辑策略" : "新增策略"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="scenario_id" label="场景 ID" rules={[{ required: true }]}>
            <Input disabled />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
                <Form.Item name="rule_mode" label="规则模式" rules={[{ required: true }]}>
                    <Select>
                        <Select.Option value={0}>0 - 超级模式 (黑/白名单优先)</Select.Option>
                        <Select.Option value={1}>1 - 自定义模式</Select.Option>
                    </Select>
                </Form.Item>
            </Col>
            <Col span={12}>
                <Form.Item name="strategy" label="处置策略 (Strategy)" rules={[{ required: true }]}>
                    <Select>
                        <Select.Option value="BLOCK">拦截 (BLOCK)</Select.Option>
                        <Select.Option value="PASS">放行 (PASS)</Select.Option>
                        <Select.Option value="REWRITE">重写 (REWRITE)</Select.Option>
                    </Select>
                </Form.Item>
            </Col>
          </Row>

          <Form.Item name="match_type" label="匹配类型" rules={[{ required: true }]}>
            <Radio.Group onChange={handleMatchTypeChange}>
                <Radio.Button value="KEYWORD">敏感词 (KEYWORD)</Radio.Button>
                <Radio.Button value="TAG">标签 (TAG)</Radio.Button>
            </Radio.Group>
          </Form.Item>

          {matchType === 'KEYWORD' ? (
             // KEYWORD MODE
             <>
                <Form.Item 
                    name="match_value" 
                    label="敏感词内容 (Match Value)" 
                    rules={[{ required: true, message: '请输入要匹配的敏感词' }]}
                    help="需要匹配的具体词汇。"
                >
                    <Input placeholder="例如：某些敏感词" />
                </Form.Item>
                <Form.Item 
                    name="extra_condition" 
                    label="关联标签 (可选)"
                    help="可选。该敏感词关联的分类标签。"
                >
                    <Select placeholder="请选择标签" allowClear showSearch optionFilterProp="children">
                        {tags.map(tag => (
                            <Select.Option key={tag.tag_code} value={tag.tag_code}>{tag.tag_name} ({tag.tag_code})</Select.Option>
                        ))}
                    </Select>
                </Form.Item>
             </>
          ) : (
             // TAG MODE
             <>
                <Form.Item 
                    name="match_value" 
                    label="标签编码 (Match Value)" 
                    rules={[{ required: true, message: '请选择标签编码' }]}
                    help="需要匹配的内容分类标签。"
                >
                    <Select placeholder="请选择标签" showSearch optionFilterProp="children">
                        {tags.map(tag => (
                            <Select.Option key={tag.tag_code} value={tag.tag_code}>{tag.tag_name} ({tag.tag_code})</Select.Option>
                        ))}
                    </Select>
                </Form.Item>
                <Form.Item 
                    name="extra_condition" 
                    label="模型判定结果 (可选)"
                    help="基于模型安全判定结果进行过滤。"
                >
                    <Select allowClear placeholder="请选择结果类型">
                        <Select.Option value="safe">safe (安全)</Select.Option>
                        <Select.Option value="unsafe">unsafe (不安全)</Select.Option>
                        <Select.Option value="controversial">controversial (有争议)</Select.Option>
                    </Select>
                </Form.Item>
             </>
          )}

          <Form.Item name="is_active" label="是否启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ScenarioPoliciesPage;
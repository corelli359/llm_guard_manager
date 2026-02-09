import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Tag, Radio, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { RuleScenarioPolicy, MetaTag } from '../types';
import { rulePoliciesApi, metaTagsApi, getErrorMessage } from '../api';

const { Search } = Input;

interface ScenarioRulesTabProps {
  scenarioId: string;
  ruleMode: number; // 0: Super, 1: Custom
  modeName: string;
}

const ScenarioRulesTab: React.FC<ScenarioRulesTabProps> = ({ scenarioId, ruleMode, modeName }) => {
  const [policies, setPolicies] = useState<RuleScenarioPolicy[]>([]);
  const [filteredPolicies, setFilteredPolicies] = useState<RuleScenarioPolicy[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [matchType, setMatchType] = useState<'KEYWORD' | 'TAG'>('KEYWORD');
  const [searchText, setSearchText] = useState<string>('');
  const [hasAccess, setHasAccess] = useState<boolean>(true);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchPolicies();
    fetchTags();
  }, [scenarioId, ruleMode]);

  useEffect(() => {
    applyFilters();
  }, [policies, searchText]);

  const fetchTags = async () => {
    try {
      const res = await metaTagsApi.getAll();
      setTags(res.data);
    } catch (error) {
      console.error('Failed to fetch tags', error);
    }
  };

  const fetchPolicies = async () => {
    if (!scenarioId) return;
    setLoading(true);
    try {
      const res = await rulePoliciesApi.getByScenario(scenarioId);
      // Filter by rule_mode
      const filtered = res.data.filter((p: RuleScenarioPolicy) => p.rule_mode === ruleMode);
      setPolicies(filtered);
      setHasAccess(true);
    } catch (error: any) {
      if (error.response?.status === 403) {
        setHasAccess(false);
      }
      message.error(getErrorMessage(error, '获取策略列表失败'));
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...policies];

    // Filter by search text (match_value or strategy)
    if (searchText.trim()) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(p =>
        p.match_value.toLowerCase().includes(searchLower) ||
        p.strategy.toLowerCase().includes(searchLower)
      );
    }

    setFilteredPolicies(filtered);
  };

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setMatchType('KEYWORD');
    form.setFieldsValue({
      scenario_id: scenarioId,
      is_active: true,
      rule_mode: ruleMode,
      match_type: 'KEYWORD',
      strategy: 'BLOCK'
    });
    setIsModalOpen(true);
  };

  const handleEdit = (record: RuleScenarioPolicy) => {
    setEditingId(record.id);
    setMatchType(record.match_type);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await rulePoliciesApi.delete(id);
      message.success('策略已删除');
      fetchPolicies();
    } catch (error: any) {
      message.error(getErrorMessage(error, '删除失败'));
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
      fetchPolicies();
    } catch (error: any) {
      console.error(error);
      if (error.errorFields) {
        // Form validation error, do nothing
      } else {
        message.error(getErrorMessage(error, '操作失败'));
      }
    }
  };

  const handleMatchTypeChange = (e: any) => {
    setMatchType(e.target.value);
    form.setFieldsValue({ match_value: '', extra_condition: '' });
  };

  const columns = [
    {
      title: '匹配类型',
      dataIndex: 'match_type',
      key: 'match_type',
      width: 120,
      render: (val: string) => <Tag color={val === 'KEYWORD' ? 'blue' : 'purple'}>{val === 'KEYWORD' ? '敏感词' : '标签'}</Tag>
    },
    {
      title: '匹配内容',
      dataIndex: 'match_value',
      key: 'match_value',
      width: 200,
    },
    {
      title: '额外条件',
      dataIndex: 'extra_condition',
      key: 'extra_condition',
      width: 150,
      render: (text: string) => text || '-'
    },
    {
      title: '处置策略',
      dataIndex: 'strategy',
      key: 'strategy',
      width: 150,
      render: (val: string) => {
        let color = 'default';
        let text = val;
        if (val === 'BLOCK') { color = 'red'; text = '拦截'; }
        if (val === 'PASS') { color = 'green'; text = '放行'; }
        if (val === 'REWRITE') { color = 'orange'; text = '重写'; }
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '是否启用',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: RuleScenarioPolicy) => hasAccess ? (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} size="small" />
          <Popconfirm title="确定要删除此策略吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button icon={<DeleteOutlined />} danger size="small" />
          </Popconfirm>
        </Space>
      ) : <Tag color="default">无权限</Tag>,
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }} align="middle">
        <Col flex="auto">
          <span style={{ color: '#666' }}>当前模式: <Tag color="blue">{modeName}</Tag></span>
        </Col>
        <Col>
          <Search
            placeholder="搜索匹配值或策略"
            allowClear
            style={{ width: 250 }}
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
          />
        </Col>
        <Col>
          {hasAccess && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增规则
            </Button>
          )}
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={filteredPolicies}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (total) => `共 ${total} 条` }}
      />

      <Modal
        title={editingId ? "编辑规则" : "新增规则"}
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

          <Form.Item name="rule_mode" label="规则模式" rules={[{ required: true }]}>
            <Select disabled>
              <Select.Option value={0}>超级模式</Select.Option>
              <Select.Option value={1}>自定义模式</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="match_type" label="匹配类型" rules={[{ required: true }]}>
            <Radio.Group onChange={handleMatchTypeChange}>
              <Radio.Button value="KEYWORD">敏感词 (KEYWORD)</Radio.Button>
              <Radio.Button value="TAG">标签 (TAG)</Radio.Button>
            </Radio.Group>
          </Form.Item>

          {matchType === 'KEYWORD' ? (
            <>
              <Form.Item
                name="match_value"
                label="敏感词内容"
                rules={[{ required: true, message: '请输入要匹配的敏感词' }]}
                help="需要匹配的具体词汇（应在敏感词管理中已配置）"
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
            <>
              <Form.Item
                name="match_value"
                label="标签编码"
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

          <Form.Item name="strategy" label="处置策略" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="BLOCK">拦截 (BLOCK)</Select.Option>
              <Select.Option value="PASS">放行 (PASS)</Select.Option>
              <Select.Option value="REWRITE">重写 (REWRITE)</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="is_active" label="是否启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ScenarioRulesTab;

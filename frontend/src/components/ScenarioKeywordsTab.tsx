import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Tag, Radio, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import { ScenarioKeyword, MetaTag } from '../types';
import { scenarioKeywordsApi, metaTagsApi } from '../api';

const { Option } = Select;
const { Search } = Input;

interface ScenarioKeywordsTabProps {
  scenarioId: string;
  mode: 'custom' | 'super';
}

const ScenarioKeywordsTab: React.FC<ScenarioKeywordsTabProps> = ({ scenarioId, mode }) => {
  const [searchParams] = useSearchParams();
  const [keywords, setKeywords] = useState<ScenarioKeyword[]>([]);
  const [filteredKeywords, setFilteredKeywords] = useState<ScenarioKeyword[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<'all' | 0 | 1>('all');
  const [searchText, setSearchText] = useState<string>('');
  const [form] = Form.useForm();

  const ruleMode = mode === 'custom' ? 1 : 0;

  useEffect(() => {
    const cat = searchParams.get('category');
    if (cat === '0') setCategoryFilter(0);
    else if (cat === '1') setCategoryFilter(1);
    else if (!cat) setCategoryFilter('all');
  }, [searchParams]);

  useEffect(() => {
    fetchKeywords();
    fetchTags();
  }, [scenarioId, mode]);

  useEffect(() => {
    applyFilters();
  }, [keywords, categoryFilter, searchText]);

  const fetchKeywords = async () => {
    if (!scenarioId) return;
    setLoading(true);
    try {
      const res = await scenarioKeywordsApi.getByScenario(scenarioId, ruleMode);
      setKeywords(res.data);
    } catch (error) {
      message.error('获取场景敏感词失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const res = await metaTagsApi.getAll();
      setTags(res.data);
    } catch (error) {
      message.error('获取标签列表失败');
    }
  };

  const applyFilters = () => {
    let filtered = [...keywords];

    // Filter by category
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(k => k.category === categoryFilter);
    }

    // Filter by search text
    if (searchText.trim()) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(k => k.keyword.toLowerCase().includes(searchLower));
    }

    setFilteredKeywords(filtered);
  };

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({
      scenario_id: scenarioId,
      is_active: true,
      category: 1, // Default to blacklist
      rule_mode: ruleMode,
      risk_level: 'High'
    });
    setIsModalOpen(true);
  };

  const handleEdit = (record: ScenarioKeyword) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await scenarioKeywordsApi.delete(id);
      message.success('敏感词已删除');
      fetchKeywords();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await scenarioKeywordsApi.update(editingId, values);
        message.success('敏感词已更新');
      } else {
        await scenarioKeywordsApi.create(values);
        message.success('敏感词已成功添加');
      }
      setIsModalOpen(false);
      fetchKeywords();
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

  const columns = [
    {
      title: '敏感词内容',
      dataIndex: 'keyword',
      key: 'keyword',
      width: 200,
    },
    {
      title: '名单类型',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (val: number) => val === 0 ? <Tag color="green">白名单</Tag> : <Tag color="red">黑名单</Tag>
    },
    {
      title: '关联标签',
      dataIndex: 'tag_code',
      key: 'tag_code',
      width: 150,
      render: (text: string) => text ? <Tag color="blue">{text}</Tag> : '-'
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      width: 120,
      render: (level: string) => {
        let color = 'default';
        if (level === 'High') color = 'red';
        if (level === 'Medium') color = 'orange';
        if (level === 'Low') color = 'green';
        return level ? <Tag color={color}>{level}</Tag> : '-';
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
      render: (_: any, record: ScenarioKeyword) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} size="small" />
          <Popconfirm title="确定要删除吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button icon={<DeleteOutlined />} danger size="small" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }} align="middle">
        <Col flex="auto">
          <Space>
            <span>过滤:</span>
            <Radio.Group value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
              <Radio.Button value="all">全部</Radio.Button>
              <Radio.Button value={1}>仅黑名单</Radio.Button>
              <Radio.Button value={0}>仅白名单</Radio.Button>
            </Radio.Group>
          </Space>
        </Col>
        <Col>
          <Search
            placeholder="搜索敏感词"
            allowClear
            style={{ width: 250 }}
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
          />
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            添加敏感词
          </Button>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={filteredKeywords}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (total) => `共 ${total} 条` }}
      />

      <Modal
        title={editingId ? "编辑敏感词" : "添加敏感词"}
        open={isModalOpen}
        onOk={handleOk}
        onCancel={() => setIsModalOpen(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="scenario_id" label="场景 ID" rules={[{ required: true }]}>
            <Input disabled />
          </Form.Item>
          <Form.Item name="rule_mode" hidden>
            <Input />
          </Form.Item>
          <Form.Item name="keyword" label="敏感词内容" rules={[{ required: true, message: '请输入敏感词' }]}>
            <Input placeholder="例如：某些敏感词汇" />
          </Form.Item>
          <Form.Item name="category" label="名单类型" rules={[{ required: true }]}>
            <Select>
              <Select.Option value={1}>黑名单 (Block)</Select.Option>
              <Select.Option value={0}>白名单 (Allow)</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item 
            name="tag_code" 
            label="关联标签 (Tag Code)"
            rules={[{ required: true, message: '必须选择标签' }]}
          >
            <Select placeholder="请选择标签" showSearch optionFilterProp="children" allowClear>
              {tags.map(tag => (
                <Option key={tag.tag_code} value={tag.tag_code}>{tag.tag_name} ({tag.tag_code})</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="risk_level" label="风险等级">
            <Select placeholder="选择风险等级">
              <Select.Option value="High">高 (High)</Select.Option>
              <Select.Option value="Medium">中 (Medium)</Select.Option>
              <Select.Option value="Low">低 (Low)</Select.Option>
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

export default ScenarioKeywordsTab;

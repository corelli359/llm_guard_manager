import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Card, Row, Col, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { ScenarioKeyword, MetaTag } from '../types';
import { scenarioKeywordsApi, metaTagsApi } from '../api';

const { Option } = Select;

const ScenarioKeywordsPage: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [keywords, setKeywords] = useState<ScenarioKeyword[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [currentScenarioId, setCurrentScenarioId] = useState<string>('');
  const [searchScenarioId, setSearchScenarioId] = useState<string>('');
  const [form] = Form.useForm();

  // Initial load from URL
  useEffect(() => {
    if (appId) {
      setCurrentScenarioId(appId);
      setSearchScenarioId(appId);
      fetchKeywords(appId);
    }
    fetchTags();
  }, [appId, searchParams]); // Added searchParams to re-filter if category changes

  const fetchKeywords = async (scenarioId: string) => {
    if (!scenarioId) return;
    setLoading(true);
    try {
      const res = await scenarioKeywordsApi.getByScenario(scenarioId);
      let data = res.data;
      
      // Optional: Client-side filter by category if provided in query param
      const categoryParam = searchParams.get('category');
      if (categoryParam !== null) {
          data = data.filter(k => k.category === parseInt(categoryParam));
      }

      setKeywords(data);
      setCurrentScenarioId(scenarioId);
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

  const handleSearch = () => {
    if (searchScenarioId.trim()) {
      fetchKeywords(searchScenarioId.trim());
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
    
    // Default category from query param if available
    const catParam = searchParams.get('category');
    const defaultCat = catParam ? parseInt(catParam) : 1;

    form.setFieldsValue({ 
      scenario_id: currentScenarioId,
      is_active: true, 
      category: defaultCat, 
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
      if (currentScenarioId) fetchKeywords(currentScenarioId);
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
      if (currentScenarioId) fetchKeywords(currentScenarioId);
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    { title: '场景 ID', dataIndex: 'scenario_id', key: 'scenario_id' },
    { title: '敏感词内容', dataIndex: 'keyword', key: 'keyword' },
    { 
      title: '名单类型', 
      dataIndex: 'category', 
      key: 'category',
      render: (val: number) => val === 0 ? <Tag color="green">白名单 (Allow)</Tag> : <Tag color="red">黑名单 (Block)</Tag>
    },
    { title: '关联标签', dataIndex: 'tag_code', key: 'tag_code', render: (text: string) => text ? <Tag color="blue">{text}</Tag> : '-' },
    { 
      title: '风险等级', 
      dataIndex: 'risk_level', 
      key: 'risk_level',
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
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ScenarioKeyword) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定要删除吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
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
        <h2>场景敏感词库 {appId ? `- ${appId}` : ''}</h2>
        
        {!appId && (
            <Card title="选择场景">
            <Row gutter={16} align="middle">
                <Col>
                <span>场景 ID (Scenario ID): </span>
                </Col>
                <Col flex="auto">
                <Input 
                    placeholder="请输入场景 ID (如：chat_bot_01)" 
                    value={searchScenarioId}
                    onChange={e => setSearchScenarioId(e.target.value)}
                    onPressEnter={handleSearch}
                />
                </Col>
                <Col>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                    加载配置
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
              添加敏感词 ({currentScenarioId})
            </Button>
          </div>
          <Table 
            columns={columns} 
            dataSource={keywords} 
            rowKey="id" 
            loading={loading}
          />
        </>
      )}

      <Modal 
        title={editingId ? "编辑敏感词" : "添加敏感词"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="scenario_id" label="场景 ID" rules={[{ required: true }]}>
            <Input disabled />
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
          <Form.Item name="tag_code" label="关联标签 (Tag Code)">
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

export default ScenarioKeywordsPage;

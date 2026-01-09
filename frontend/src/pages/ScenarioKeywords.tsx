import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Card, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { ScenarioKeyword } from '../types';
import { scenarioKeywordsApi } from '../api';

const ScenarioKeywordsPage: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [keywords, setKeywords] = useState<ScenarioKeyword[]>([]);
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
  }, [appId]);

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
      message.error('Failed to fetch scenario keywords');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchScenarioId.trim()) {
      // If we are in "standalone" mode (no appId in URL), just fetch
      // If we are in "app context" mode, we might want to navigate or just fetch. 
      // For simplicity, just fetch.
      fetchKeywords(searchScenarioId.trim());
    } else {
      message.warning('Please enter a Scenario ID');
    }
  };

  const handleAdd = () => {
    if (!currentScenarioId) {
      message.warning('Please select a scenario first');
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
      message.success('Keyword deleted');
      if (currentScenarioId) fetchKeywords(currentScenarioId);
    } catch (error) {
      message.error('Failed to delete keyword');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await scenarioKeywordsApi.update(editingId, values);
        message.success('Keyword updated');
      } else {
        await scenarioKeywordsApi.create(values);
        message.success('Keyword created');
      }
      setIsModalOpen(false);
      if (currentScenarioId) fetchKeywords(currentScenarioId);
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    { title: 'Scenario ID', dataIndex: 'scenario_id', key: 'scenario_id' },
    { title: 'Keyword', dataIndex: 'keyword', key: 'keyword' },
    { 
      title: 'Category', 
      dataIndex: 'category', 
      key: 'category',
      render: (val: number) => val === 0 ? <span style={{color: 'green'}}>Whitelist</span> : <span style={{color: 'red'}}>Blacklist</span>
    },
    { title: 'Tag Code', dataIndex: 'tag_code', key: 'tag_code' },
    { title: 'Risk Level', dataIndex: 'risk_level', key: 'risk_level' },
    {
      title: 'Active',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: ScenarioKeyword) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record.id)}>
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
                Back to App Dashboard
            </Button>
        )}
        <h2>Scenario Keywords {appId ? `for ${appId}` : ''}</h2>
        
        {!appId && (
            <Card>
            <Row gutter={16} align="middle">
                <Col>
                <span>Scenario ID: </span>
                </Col>
                <Col flex="auto">
                <Input 
                    placeholder="Enter Scenario ID (e.g. chat_bot_01)" 
                    value={searchScenarioId}
                    onChange={e => setSearchScenarioId(e.target.value)}
                    onPressEnter={handleSearch}
                />
                </Col>
                <Col>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                    Load Config
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
              Add Keyword to {currentScenarioId}
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
        title={editingId ? "Edit Keyword" : "Add New Keyword"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="scenario_id" label="Scenario ID" rules={[{ required: true }]}>
            <Input disabled />
          </Form.Item>
          <Form.Item name="keyword" label="Keyword" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="category" label="Category" rules={[{ required: true }]}>
            <Select>
              <Select.Option value={1}>Blacklist (Block)</Select.Option>
              <Select.Option value={0}>Whitelist (Allow)</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="tag_code" label="Tag Code">
             <Input />
          </Form.Item>
          <Form.Item name="risk_level" label="Risk Level">
            <Select>
              <Select.Option value="High">High</Select.Option>
              <Select.Option value="Medium">Medium</Select.Option>
              <Select.Option value="Low">Low</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ScenarioKeywordsPage;

import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Card, Row, Col, Tag, Radio } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { RuleScenarioPolicy } from '../types';
import { rulePoliciesApi } from '../api';

const ScenarioPoliciesPage: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const navigate = useNavigate();

  const [policies, setPolicies] = useState<RuleScenarioPolicy[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [currentScenarioId, setCurrentScenarioId] = useState<string>('');
  const [searchScenarioId, setSearchScenarioId] = useState<string>('');
  const [matchType, setMatchType] = useState<'KEYWORD' | 'TAG'>('KEYWORD');
  
  const [form] = Form.useForm();

  // Initial load from URL
  useEffect(() => {
    if (appId) {
        setCurrentScenarioId(appId);
        setSearchScenarioId(appId);
        fetchPolicies(appId);
    }
  }, [appId]);

  const fetchPolicies = async (scenarioId: string) => {
    if (!scenarioId) return;
    setLoading(true);
    try {
      const res = await rulePoliciesApi.getByScenario(scenarioId);
      setPolicies(res.data);
      setCurrentScenarioId(scenarioId);
    } catch (error) {
      message.error('Failed to fetch policies');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchScenarioId.trim()) {
      fetchPolicies(searchScenarioId.trim());
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
      message.success('Policy deleted');
      if (currentScenarioId) fetchPolicies(currentScenarioId);
    } catch (error) {
      message.error('Failed to delete policy');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await rulePoliciesApi.update(editingId, values);
        message.success('Policy updated');
      } else {
        await rulePoliciesApi.create(values);
        message.success('Policy created');
      }
      setIsModalOpen(false);
      if (currentScenarioId) fetchPolicies(currentScenarioId);
    } catch (error) {
      console.error(error);
    }
  };

  const handleMatchTypeChange = (e: any) => {
    setMatchType(e.target.value);
    // Optional: Clear dependent fields when switching type
    form.setFieldsValue({ match_value: '', extra_condition: '' });
  };

  const columns = [
    { title: 'Rule Mode', dataIndex: 'rule_mode', key: 'rule_mode', 
      render: (val: number) => val === 0 ? <Tag color="gold">Super (0)</Tag> : <Tag color="blue">Custom (1)</Tag>
    },
    { title: 'Match Type', dataIndex: 'match_type', key: 'match_type',
      render: (val: string) => <Tag>{val}</Tag>
    },
    { title: 'Match Value', dataIndex: 'match_value', key: 'match_value' },
    { title: 'Extra Condition', dataIndex: 'extra_condition', key: 'extra_condition' },
    { title: 'Strategy', dataIndex: 'strategy', key: 'strategy',
      render: (val: string) => {
        let color = 'default';
        if (val === 'BLOCK') color = 'red';
        if (val === 'PASS') color = 'green';
        if (val === 'REWRITE') color = 'orange';
        return <Tag color={color}>{val}</Tag>;
      }
    },
    {
      title: 'Active',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: RuleScenarioPolicy) => (
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
        <h2>Scenario Policies {appId ? `for ${appId}` : ''}</h2>
        {!appId && (
            <Card>
            <Row gutter={16} align="middle">
                <Col>
                <span>Scenario ID: </span>
                </Col>
                <Col flex="auto">
                <Input 
                    placeholder="Enter Scenario ID" 
                    value={searchScenarioId}
                    onChange={e => setSearchScenarioId(e.target.value)}
                    onPressEnter={handleSearch}
                />
                </Col>
                <Col>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                    Load Policies
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
              Add Policy to {currentScenarioId}
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
        title={editingId ? "Edit Policy" : "Add New Policy"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="scenario_id" label="Scenario ID" rules={[{ required: true }]}>
            <Input disabled />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
                <Form.Item name="rule_mode" label="Rule Mode" rules={[{ required: true }]}>
                    <Select>
                        <Select.Option value={0}>0 - Super (Black/White)</Select.Option>
                        <Select.Option value={1}>1 - Custom</Select.Option>
                    </Select>
                </Form.Item>
            </Col>
            <Col span={12}>
                <Form.Item name="strategy" label="Strategy" rules={[{ required: true }]}>
                    <Select>
                        <Select.Option value="BLOCK">BLOCK</Select.Option>
                        <Select.Option value="PASS">PASS</Select.Option>
                        <Select.Option value="REWRITE">REWRITE</Select.Option>
                    </Select>
                </Form.Item>
            </Col>
          </Row>

          <Form.Item name="match_type" label="Match Type" rules={[{ required: true }]}>
            <Radio.Group onChange={handleMatchTypeChange}>
                <Radio.Button value="KEYWORD">KEYWORD</Radio.Button>
                <Radio.Button value="TAG">TAG</Radio.Button>
            </Radio.Group>
          </Form.Item>

          {matchType === 'KEYWORD' ? (
             // KEYWORD MODE
             <>
                <Form.Item 
                    name="match_value" 
                    label="Keyword (Match Value)" 
                    rules={[{ required: true, message: 'Please input the keyword' }]}
                    help="The sensitive word to match."
                >
                    <Input placeholder="e.g. sensitive_word" />
                </Form.Item>
                <Form.Item 
                    name="extra_condition" 
                    label="Related Tag (Extra Condition)"
                    help="Optional. The tag code associated with this keyword."
                >
                    <Input placeholder="e.g. POLITICAL" />
                </Form.Item>
             </>
          ) : (
             // TAG MODE
             <>
                <Form.Item 
                    name="match_value" 
                    label="Tag Code (Match Value)" 
                    rules={[{ required: true, message: 'Please input the Tag Code' }]}
                    help="The content classification tag to match."
                >
                    <Input placeholder="e.g. VIOLENCE" />
                </Form.Item>
                <Form.Item 
                    name="extra_condition" 
                    label="Model Judgement (Extra Condition)"
                    help="Filter by the model's safety judgement result."
                >
                    <Select allowClear>
                        <Select.Option value="safe">safe</Select.Option>
                        <Select.Option value="unsafe">unsafe</Select.Option>
                        <Select.Option value="controversial">controversial</Select.Option>
                    </Select>
                </Form.Item>
             </>
          )}

          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ScenarioPoliciesPage;

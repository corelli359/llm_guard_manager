import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Switch, Space, message, Popconfirm, Card, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, AppstoreOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ScenarioApp } from '../types';
import { scenariosApi } from '../api';

const AppsPage: React.FC = () => {
  const [apps, setApps] = useState<ScenarioApp[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const fetchApps = async () => {
    setLoading(true);
    try {
      const res = await scenariosApi.getAll();
      setApps(res.data);
    } catch (error) {
      message.error('Failed to fetch apps');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApps();
  }, []);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({ 
      is_active: true, 
      enable_whitelist: true, 
      enable_blacklist: true, 
      enable_custom_policy: true 
    });
    setIsModalOpen(true);
  };

  const handleEdit = (record: ScenarioApp) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await scenariosApi.delete(id);
      message.success('App deleted');
      fetchApps();
    } catch (error) {
      message.error('Failed to delete app');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await scenariosApi.update(editingId, values);
        message.success('App updated');
      } else {
        await scenariosApi.create(values);
        message.success('App created');
      }
      setIsModalOpen(false);
      fetchApps();
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    { title: 'App ID', dataIndex: 'app_id', key: 'app_id', render: (text: string) => <b>{text}</b> },
    { title: 'App Name', dataIndex: 'app_name', key: 'app_name' },
    { title: 'Active', dataIndex: 'is_active', key: 'is_active', render: (val: boolean) => <Switch size="small" checked={val} disabled /> },
    { 
      title: 'Features', 
      key: 'features',
      render: (_: any, record: ScenarioApp) => (
        <Space size="small">
          {record.enable_blacklist && <Tag color="red">Blacklist</Tag>}
          {record.enable_whitelist && <Tag color="green">Whitelist</Tag>}
          {record.enable_custom_policy && <Tag color="blue">Policies</Tag>}
        </Space>
      )
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: ScenarioApp) => (
        <Space size="middle">
          <Button type="link" icon={<AppstoreOutlined />} onClick={() => navigate(`/apps/${record.app_id}`)}>
            Manage
          </Button>
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
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>App Management</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Register New App
        </Button>
      </div>

      <Table 
        columns={columns} 
        dataSource={apps} 
        rowKey="id" 
        loading={loading}
      />

      <Modal 
        title={editingId ? "Edit App" : "Register New App"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="app_id" label="App ID (Unique)" rules={[{ required: true }]}>
            <Input disabled={!!editingId} placeholder="e.g. chat_bot_01" />
          </Form.Item>
          <Form.Item name="app_name" label="App Name" rules={[{ required: true }]}>
            <Input placeholder="e.g. Customer Service Bot" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea />
          </Form.Item>
          
          <Card size="small" title="Feature Flags" style={{ marginTop: 16 }}>
             <Form.Item name="is_active" label="App Active" valuePropName="checked">
                <Switch />
             </Form.Item>
             <Form.Item name="enable_blacklist" label="Enable Blacklist Keywords" valuePropName="checked">
                <Switch />
             </Form.Item>
             <Form.Item name="enable_whitelist" label="Enable Whitelist Keywords" valuePropName="checked">
                <Switch />
             </Form.Item>
             <Form.Item name="enable_custom_policy" label="Enable Custom Policies" valuePropName="checked">
                <Switch />
             </Form.Item>
          </Card>
        </Form>
      </Modal>
    </div>
  );
};

export default AppsPage;

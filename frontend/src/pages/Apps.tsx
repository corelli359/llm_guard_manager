import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Switch, Space, message, Popconfirm, Card, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, AppstoreOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { ScenarioApp } from '../types';
import { scenariosApi, getErrorMessage } from '../api';

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
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取应用列表失败'));
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
      message.success('应用已注销');
      fetchApps();
    } catch (error: any) {
      message.error(getErrorMessage(error, '删除失败'));
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await scenariosApi.update(editingId, values);
        message.success('应用信息已更新');
      } else {
        await scenariosApi.create(values);
        message.success('应用已成功注册');
      }
      setIsModalOpen(false);
      fetchApps();
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    { title: '应用 ID (App ID)', dataIndex: 'app_id', key: 'app_id', render: (text: string) => <b>{text}</b> },
    { title: '应用名称', dataIndex: 'app_name', key: 'app_name' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (val: boolean) => <Switch size="small" checked={val} disabled /> },
    { 
      title: '功能模块', 
      key: 'features',
      render: (_: any, record: ScenarioApp) => (
        <Space size="small">
          {record.enable_blacklist && <Tag color="red">黑名单</Tag>}
          {record.enable_whitelist && <Tag color="green">白名单</Tag>}
          {record.enable_custom_policy && <Tag color="blue">自定义策略</Tag>}
        </Space>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ScenarioApp) => (
        <Space size="middle">
          <Button type="link" icon={<AppstoreOutlined />} onClick={() => navigate(`/apps/${record.app_id}`)}>
            进入管理
          </Button>
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定注销该应用吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>应用管理 (App Management)</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          注册新应用
        </Button>
      </div>

      <Table 
        columns={columns} 
        dataSource={apps} 
        rowKey="id" 
        loading={loading}
      />

      <Modal 
        title={editingId ? "编辑应用" : "注册新应用"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="app_id" label="应用唯一标识 (App ID)" rules={[{ required: true, message: '请输入应用 ID' }]}>
            <Input disabled={!!editingId} placeholder="例如：chat_bot_01" />
          </Form.Item>
          <Form.Item name="app_name" label="应用名称" rules={[{ required: true, message: '请输入应用名称' }]}>
            <Input placeholder="例如：智能客服助手" />
          </Form.Item>
          <Form.Item name="description" label="应用描述">
            <Input.TextArea placeholder="可选：简要描述应用用途" />
          </Form.Item>
          
          <Card size="small" title="功能开关" style={{ marginTop: 16 }}>
             <Form.Item name="is_active" label="激活应用" valuePropName="checked">
                <Switch />
             </Form.Item>
             <Form.Item name="enable_blacklist" label="启用敏感词黑名单" valuePropName="checked">
                <Switch />
             </Form.Item>
             <Form.Item name="enable_whitelist" label="启用白名单" valuePropName="checked">
                <Switch />
             </Form.Item>
             <Form.Item name="enable_custom_policy" label="启用自定义处置策略" valuePropName="checked">
                <Switch />
             </Form.Item>
          </Card>
        </Form>
      </Modal>
    </div>
  );
};

export default AppsPage;
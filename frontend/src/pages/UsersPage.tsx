import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, message, Tag, Space, Popconfirm, Switch } from 'antd';
import { UserAddOutlined, CopyOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { usersApi } from '../api';
import dayjs from 'dayjs';

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [credentials, setCredentials] = useState<{username: string, password: string, isReset?: boolean} | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await usersApi.list();
      setUsers(res.data);
    } catch (error) {
      message.error('获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (values: any) => {
    try {
      const res = await usersApi.create(values);
      setCredentials(res.data);
      message.success('用户创建成功');
      setIsModalOpen(false);
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败');
    }
  };

  const handleStatusChange = async (id: string, checked: boolean) => {
      try {
          await usersApi.updateStatus(id, checked);
          message.success('状态已更新');
          fetchUsers();
      } catch (e) {
          message.error('更新失败');
      }
  };

  const handleResetPassword = async (id: string) => {
      try {
          const res = await usersApi.resetPassword(id);
          setCredentials({...res.data, isReset: true});
          message.success('密码已重置');
      } catch (e) {
          message.error('重置失败');
      }
  };

  const handleDelete = async (id: string) => {
      try {
          await usersApi.delete(id);
          message.success('用户已删除');
          fetchUsers();
      } catch (e) {
          message.error('删除失败');
      }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('已复制到剪贴板');
    } catch (err) {
      // 降级方案：使用传统方法
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        message.success('已复制到剪贴板');
      } catch (e) {
        message.error('复制失败，请手动复制');
      }
      document.body.removeChild(textArea);
    }
  };

  const columns = [
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '角色', dataIndex: 'role', key: 'role', render: (role: string) => <Tag color={role === 'ADMIN' ? 'gold' : 'blue'}>{role}</Tag> },
    { 
        title: '状态', 
        dataIndex: 'is_active', 
        key: 'is_active', 
        render: (active: boolean, record: any) => (
            <Switch 
                checked={active} 
                onChange={(checked) => handleStatusChange(record.id, checked)}
                checkedChildren="Active"
                unCheckedChildren="Inactive"
                disabled={record.role === 'ADMIN'} 
            />
        ) 
    },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', render: (d: string) => dayjs(d).format('YYYY-MM-DD HH:mm') },
    {
        title: '操作',
        key: 'action',
        render: (_: any, record: any) => (
            <Space>
                <Popconfirm title="确定重置密码吗?" onConfirm={() => handleResetPassword(record.id)}>
                    <Button size="small" icon={<ReloadOutlined />}>重置密码</Button>
                </Popconfirm>
                <Popconfirm title="确定删除用户吗?" onConfirm={() => handleDelete(record.id)} disabled={record.role === 'ADMIN'}>
                    <Button size="small" danger icon={<DeleteOutlined />} disabled={record.role === 'ADMIN'} />
                </Popconfirm>
            </Space>
        )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>用户管理 (User Management)</h2>
        <Button type="primary" icon={<UserAddOutlined />} onClick={() => { setCredentials(null); setIsModalOpen(true); form.resetFields(); }}>
          新建审核员
        </Button>
      </div>

      <Table dataSource={users} columns={columns} rowKey="id" loading={loading} />

      {/* Create User Modal */}
      <Modal
        title="新建审核员"
        open={isModalOpen}
        onOk={() => form.submit()}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input placeholder="例如: auditor_01" />
          </Form.Item>
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                <Button onClick={() => setIsModalOpen(false)}>取消</Button>
                <Button type="primary" htmlType="submit">创建并生成密码</Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>

      {/* Credentials Modal */}
      <Modal
        title={<span style={{color: '#52c41a'}}>{credentials?.isReset ? '密码重置成功' : '账号创建成功'}</span>}
        open={!!credentials}
        onCancel={() => setCredentials(null)}
        footer={[
            <Button key="close" type="primary" onClick={() => setCredentials(null)}>
                我已保存
            </Button>
        ]}
      >
        {credentials && (
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <p style={{ fontSize: 16 }}>用户名: <strong>{credentials.username}</strong></p>
                <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 8, margin: '16px 0' }}>
                    <p style={{ color: '#888', marginBottom: 8 }}>{credentials.isReset ? '新密码' : '初始密码'}</p>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                        <Tag style={{ fontSize: 20, padding: '6px 12px', margin: 0 }} color="blue">{credentials.password}</Tag>
                        <Button icon={<CopyOutlined />} onClick={() => copyToClipboard(credentials.password)}>复制</Button>
                    </div>
                </div>
                <p style={{ color: '#faad14', margin: 0 }}>注意：密码仅显示一次，请务必发送给相关人员。</p>
            </div>
        )}
      </Modal>
    </div>
  );
};

export default UsersPage;
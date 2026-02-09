import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Tag, Space, Popconfirm, message, Card, Checkbox } from 'antd';
import { PlusOutlined, SettingOutlined } from '@ant-design/icons';
import { rolesApi, getErrorMessage } from '../api';
import { Role, PermissionItem } from '../types';
import dayjs from 'dayjs';

const RolesPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [allPermissions, setAllPermissions] = useState<PermissionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [permModalOpen, setPermModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [selectedPermIds, setSelectedPermIds] = useState<string[]>([]);
  const [createForm] = Form.useForm();
  const [editForm] = Form.useForm();

  useEffect(() => {
    fetchRoles();
    fetchAllPermissions();
  }, []);

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const res = await rolesApi.list();
      setRoles(res.data);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取角色列表失败'));
    } finally {
      setLoading(false);
    }
  };

  const fetchAllPermissions = async () => {
    try {
      const res = await rolesApi.listAllPermissions();
      setAllPermissions(res.data);
    } catch {
      console.error('Failed to fetch permissions');
    }
  };

  const handleCreate = async (values: any) => {
    try {
      await rolesApi.create(values);
      message.success('角色创建成功');
      setCreateModalOpen(false);
      createForm.resetFields();
      fetchRoles();
    } catch (error: any) {
      message.error(getErrorMessage(error, '创建失败'));
    }
  };

  const handleEdit = async (values: any) => {
    if (!selectedRole) return;
    try {
      await rolesApi.update(selectedRole.id, values);
      message.success('角色更新成功');
      setEditModalOpen(false);
      fetchRoles();
    } catch (error: any) {
      message.error(getErrorMessage(error, '更新失败'));
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await rolesApi.delete(id);
      message.success('角色已删除');
      fetchRoles();
    } catch (error: any) {
      message.error(getErrorMessage(error, '删除失败'));
    }
  };

  const openEditModal = (role: Role) => {
    setSelectedRole(role);
    editForm.setFieldsValue({
      role_name: role.role_name,
      role_type: role.role_type,
      description: role.description,
    });
    setEditModalOpen(true);
  };

  const openPermModal = async (role: Role) => {
    setSelectedRole(role);
    try {
      const res = await rolesApi.getPermissions(role.id);
      const permIds = res.data.map((p: PermissionItem) => p.id);
      setSelectedPermIds(permIds);
      setPermModalOpen(true);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取角色权限失败'));
    }
  };

  const handleSavePermissions = async () => {
    if (!selectedRole) return;
    try {
      await rolesApi.updatePermissions(selectedRole.id, selectedPermIds);
      message.success('权限配置成功');
      setPermModalOpen(false);
      fetchRoles();
    } catch (error: any) {
      message.error(getErrorMessage(error, '配置失败'));
    }
  };

  const globalPerms = allPermissions.filter(p => p.scope === 'GLOBAL');
  const scenarioPerms = allPermissions.filter(p => p.scope === 'SCENARIO');

  const columns = [
    { title: '角色名称', dataIndex: 'role_name', key: 'role_name' },
    { title: '角色编码', dataIndex: 'role_code', key: 'role_code' },
    {
      title: '类型',
      dataIndex: 'role_type',
      key: 'role_type',
      render: (t: string) => (
        <Tag color={t === 'GLOBAL' ? 'blue' : 'green'}>{t === 'GLOBAL' ? '全局' : '场景'}</Tag>
      ),
    },
    {
      title: '权限数量',
      dataIndex: 'permission_count',
      key: 'permission_count',
    },
    {
      title: '系统角色',
      dataIndex: 'is_system',
      key: 'is_system',
      render: (v: boolean) => v ? <Tag color="red">系统</Tag> : <Tag>自定义</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (d: string) => dayjs(d).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Role) => (
        <Space>
          <Button size="small" onClick={() => openEditModal(record)}>编辑</Button>
          <Button size="small" icon={<SettingOutlined />} onClick={() => openPermModal(record)}>配置权限</Button>
          {!record.is_system && (
            <Popconfirm title="确定删除该角色吗?" onConfirm={() => handleDelete(record.id)}>
              <Button size="small" danger>删除</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>角色管理</h2>
          <p style={{ color: '#666' }}>管理系统角色和权限配置。</p>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { createForm.resetFields(); setCreateModalOpen(true); }}>
          创建角色
        </Button>
      </div>

      <Table dataSource={roles} columns={columns} rowKey="id" loading={loading} />

      <Modal title="创建角色" open={createModalOpen} onCancel={() => setCreateModalOpen(false)} footer={null}>
        <Form form={createForm} onFinish={handleCreate} layout="vertical">
          <Form.Item name="role_code" label="角色编码" rules={[{ required: true, message: '请输入角色编码' }]}>
            <Input placeholder="如: CONTENT_REVIEWER" />
          </Form.Item>
          <Form.Item name="role_name" label="角色名称" rules={[{ required: true, message: '请输入角色名称' }]}>
            <Input placeholder="如: 内容审核员" />
          </Form.Item>
          <Form.Item name="role_type" label="角色类型" rules={[{ required: true, message: '请选择角色类型' }]}>
            <Select placeholder="请选择">
              <Select.Option value="GLOBAL">全局角色</Select.Option>
              <Select.Option value="SCENARIO">场景角色</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="角色描述" />
          </Form.Item>
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <Button onClick={() => setCreateModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit">创建</Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="编辑角色" open={editModalOpen} onCancel={() => setEditModalOpen(false)} footer={null}>
        <Form form={editForm} onFinish={handleEdit} layout="vertical">
          <Form.Item name="role_name" label="角色名称" rules={[{ required: true, message: '请输入角色名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="role_type" label="角色类型" rules={[{ required: true, message: '请选择角色类型' }]}>
            <Select>
              <Select.Option value="GLOBAL">全局角色</Select.Option>
              <Select.Option value="SCENARIO">场景角色</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <Button onClick={() => setEditModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit">保存</Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={`配置权限 - ${selectedRole?.role_name}`}
        open={permModalOpen}
        onCancel={() => setPermModalOpen(false)}
        onOk={handleSavePermissions}
        width={600}
      >
        <Card size="small" title="全局权限" style={{ marginBottom: 16 }}>
          <Checkbox.Group
            value={selectedPermIds}
            onChange={(vals) => {
              const scenarioSelected = selectedPermIds.filter(id => scenarioPerms.some(p => p.id === id));
              setSelectedPermIds([...scenarioSelected, ...(vals as string[])]);
            }}
          >
            <Space direction="vertical">
              {globalPerms.map(p => (
                <Checkbox key={p.id} value={p.id}>{p.permission_name} ({p.permission_code})</Checkbox>
              ))}
            </Space>
          </Checkbox.Group>
        </Card>
        <Card size="small" title="场景权限">
          <Checkbox.Group
            value={selectedPermIds}
            onChange={(vals) => {
              const globalSelected = selectedPermIds.filter(id => globalPerms.some(p => p.id === id));
              setSelectedPermIds([...globalSelected, ...(vals as string[])]);
            }}
          >
            <Space direction="vertical">
              {scenarioPerms.map(p => (
                <Checkbox key={p.id} value={p.id}>{p.permission_name} ({p.permission_code})</Checkbox>
              ))}
            </Space>
          </Checkbox.Group>
        </Card>
      </Modal>
    </div>
  );
};

export default RolesPage;

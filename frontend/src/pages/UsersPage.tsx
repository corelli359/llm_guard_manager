import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, message, Tag, Space, Popconfirm, Switch, Select, Drawer, Card } from 'antd';
import { DeleteOutlined, TeamOutlined, EyeOutlined, PlusOutlined, KeyOutlined } from '@ant-design/icons';
import { usersApi, userRolesApi, rolesApi, scenariosApi, getErrorMessage } from '../api';
import { ScenarioApp, Role, UserRoleAssignment } from '../types';
import dayjs from 'dayjs';

interface UserItem {
  id: string;
  username: string | null;
  display_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [scenarios, setScenarios] = useState<ScenarioApp[]>([]);
  const [loading, setLoading] = useState(false);
  const [assignRoleModalOpen, setAssignRoleModalOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [resetPwdModalOpen, setResetPwdModalOpen] = useState(false);
  const [rolesDrawerOpen, setRolesDrawerOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserItem | null>(null);
  const [userRoleAssignments, setUserRoleAssignments] = useState<UserRoleAssignment[]>([]);
  const [selectedRoleType, setSelectedRoleType] = useState<string>('');
  const [assignForm] = Form.useForm();
  const [createForm] = Form.useForm();
  const [resetPwdForm] = Form.useForm();

  useEffect(() => {
    fetchUsers();
    fetchRoles();
    fetchScenarios();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await usersApi.list();
      setUsers(res.data);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取用户列表失败'));
    } finally {
      setLoading(false);
    }
  };
  const fetchRoles = async () => {
    try {
      const res = await rolesApi.list();
      setRoles(res.data);
    } catch {
      console.error('Failed to fetch roles');
    }
  };

  const fetchScenarios = async () => {
    try {
      const res = await scenariosApi.getAll();
      setScenarios(res.data);
    } catch {
      console.error('Failed to fetch scenarios');
    }
  };

  const handleCreateUser = async (values: any) => {
    try {
      await usersApi.create(values);
      message.success('用户创建成功');
      setCreateModalOpen(false);
      createForm.resetFields();
      fetchUsers();
    } catch (error: any) {
      message.error(getErrorMessage(error, '创建用户失败'));
    }
  };

  const handleResetPassword = async (values: any) => {
    if (!selectedUser) return;
    try {
      await usersApi.resetPassword(selectedUser.id, values.password);
      message.success('密码重置成功');
      setResetPwdModalOpen(false);
      resetPwdForm.resetFields();
    } catch (error: any) {
      message.error(getErrorMessage(error, '重置密码失败'));
    }
  };

  const handleStatusChange = async (id: string, checked: boolean) => {
    try {
      await usersApi.updateStatus(id, checked);
      message.success('状态已更新');
      fetchUsers();
    } catch (error: any) {
      message.error(getErrorMessage(error, '更新失败'));
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await usersApi.delete(id);
      message.success('用户已删除');
      fetchUsers();
    } catch (error: any) {
      message.error(getErrorMessage(error, '删除失败'));
    }
  };

  const openAssignRoleModal = (user: UserItem) => {
    setSelectedUser(user);
    setSelectedRoleType('');
    assignForm.resetFields();
    setAssignRoleModalOpen(true);
  };

  const handleAssignRole = async (values: any) => {
    if (!selectedUser) return;
    try {
      const data: { role_id: string; scenario_id?: string } = { role_id: values.role_id };
      if (values.scenario_id) {
        data.scenario_id = values.scenario_id;
      }
      await userRolesApi.assignRole(selectedUser.id, data);
      message.success('角色分配成功');
      setAssignRoleModalOpen(false);
      fetchUsers();
    } catch (error: any) {
      message.error(getErrorMessage(error, '分配失败'));
    }
  };

  const openRolesDrawer = async (user: UserItem) => {
    setSelectedUser(user);
    try {
      const res = await userRolesApi.getUserRoles(user.id);
      setUserRoleAssignments(res.data);
      setRolesDrawerOpen(true);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取用户角色失败'));
    }
  };

  const handleRemoveRole = async (userId: string, assignmentId: string) => {
    try {
      await userRolesApi.removeRole(userId, assignmentId);
      message.success('角色已移除');
      const res = await userRolesApi.getUserRoles(userId);
      setUserRoleAssignments(res.data);
    } catch (error: any) {
      message.error(getErrorMessage(error, '移除失败'));
    }
  };

  const handleRoleSelectChange = (roleId: string) => {
    const role = roles.find(r => r.id === roleId);
    setSelectedRoleType(role?.role_type || '');
    if (role?.role_type === 'GLOBAL') {
      assignForm.setFieldValue('scenario_id', undefined);
    }
  };
  const columns = [
    { title: '用户名', dataIndex: 'username', key: 'username', render: (text: string) => text || '-' },
    { title: '姓名', dataIndex: 'display_name', key: 'display_name', render: (text: string) => text || '-' },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => {
        const colorMap: Record<string, string> = {
          SYSTEM_ADMIN: 'red',
          SCENARIO_ADMIN: 'blue',
          ANNOTATOR: 'green',
          AUDITOR: 'orange',
        };
        const labelMap: Record<string, string> = {
          SYSTEM_ADMIN: '系统管理员',
          SCENARIO_ADMIN: '场景管理员',
          ANNOTATOR: '标注员',
          AUDITOR: '审计员',
        };
        return <Tag color={colorMap[role] || 'default'}>{labelMap[role] || role}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean, record: UserItem) => (
        <Switch
          checked={active}
          onChange={(checked) => handleStatusChange(record.id, checked)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      ),
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
      render: (_: any, record: UserItem) => (
        <Space>
          <Button size="small" icon={<TeamOutlined />} onClick={() => openAssignRoleModal(record)}>
            分配角色
          </Button>
          <Button size="small" icon={<EyeOutlined />} onClick={() => openRolesDrawer(record)}>
            查看角色
          </Button>
          <Button size="small" icon={<KeyOutlined />} onClick={() => { setSelectedUser(record); resetPwdForm.resetFields(); setResetPwdModalOpen(true); }}>
            重置密码
          </Button>
          <Popconfirm title="确定删除用户吗?" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];
  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>用户管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { createForm.resetFields(); setCreateModalOpen(true); }}>
          创建用户
        </Button>
      </div>

      <Table dataSource={users} columns={columns} rowKey="id" loading={loading} scroll={{ x: 1000 }} />

      {/* 创建用户 Modal */}
      <Modal
        title="创建用户"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form form={createForm} onFinish={handleCreateUser} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }, { min: 6, message: '密码至少6位' }]}>
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          <Form.Item name="display_name" label="显示名称">
            <Input placeholder="请输入显示名称（可选）" />
          </Form.Item>
          <Form.Item name="role" label="角色" initialValue="ANNOTATOR">
            <Select>
              <Select.Option value="SYSTEM_ADMIN">系统管理员</Select.Option>
              <Select.Option value="SCENARIO_ADMIN">场景管理员</Select.Option>
              <Select.Option value="ANNOTATOR">标注员</Select.Option>
              <Select.Option value="AUDITOR">审计员</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <Button onClick={() => setCreateModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit">创建</Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>
      {/* 重置密码 Modal */}
      <Modal
        title={`重置密码 - ${selectedUser?.username}`}
        open={resetPwdModalOpen}
        onCancel={() => setResetPwdModalOpen(false)}
        footer={null}
      >
        <Form form={resetPwdForm} onFinish={handleResetPassword} layout="vertical">
          <Form.Item name="password" label="新密码" rules={[{ required: true, message: '请输入新密码' }, { min: 6, message: '密码至少6位' }]}>
            <Input.Password placeholder="请输入新密码" />
          </Form.Item>
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <Button onClick={() => setResetPwdModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit">确认重置</Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>

      {/* 分配角色 Modal */}
      <Modal
        title={`为用户 ${selectedUser?.username} 分配角色`}
        open={assignRoleModalOpen}
        onCancel={() => setAssignRoleModalOpen(false)}
        footer={null}
      >
        <Form form={assignForm} onFinish={handleAssignRole} layout="vertical">
          <Form.Item name="role_id" label="选择角色" rules={[{ required: true, message: '请选择角色' }]}>
            <Select placeholder="请选择角色" onChange={handleRoleSelectChange}>
              {roles.map((r) => (
                <Select.Option key={r.id} value={r.id}>
                  {r.role_name} ({r.role_code}) <Tag color={r.role_type === 'GLOBAL' ? 'blue' : 'green'}>{r.role_type === 'GLOBAL' ? '全局' : '场景'}</Tag>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          {selectedRoleType === 'SCENARIO' && (
            <Form.Item name="scenario_id" label="选择场景" rules={[{ required: true, message: '请选择场景' }]}>
              <Select placeholder="请选择场景">
                {scenarios.map((s) => (
                  <Select.Option key={s.app_id} value={s.app_id}>
                    {s.app_name} ({s.app_id})
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          )}
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <Button onClick={() => setAssignRoleModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit">分配</Button>
            </div>
          </Form.Item>
        </Form>
      </Modal>
      {/* 查看角色 Drawer */}
      <Drawer
        title={`用户角色列表 - ${selectedUser?.username}`}
        placement="right"
        width={600}
        open={rolesDrawerOpen}
        onClose={() => setRolesDrawerOpen(false)}
      >
        {userRoleAssignments.length === 0 ? (
          <p>该用户还没有分配任何角色</p>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {userRoleAssignments.map((assignment) => (
              <Card
                key={assignment.id}
                size="small"
                title={
                  <Space>
                    <TeamOutlined />
                    {assignment.role_name}
                    <Tag color={assignment.role_type === 'GLOBAL' ? 'blue' : 'green'}>
                      {assignment.role_type === 'GLOBAL' ? '全局' : '场景'}
                    </Tag>
                  </Space>
                }
                extra={
                  <Popconfirm
                    title="确定移除该角色吗?"
                    onConfirm={() => handleRemoveRole(selectedUser!.id, assignment.id)}
                  >
                    <Button size="small" danger>移除</Button>
                  </Popconfirm>
                }
              >
                <p><strong>角色编码:</strong> {assignment.role_code}</p>
                {assignment.scenario_id && (
                  <p><strong>场景ID:</strong> {assignment.scenario_id}</p>
                )}
                <p><strong>分配时间:</strong> {dayjs(assignment.created_at).format('YYYY-MM-DD HH:mm')}</p>
              </Card>
            ))}
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default UsersPage;
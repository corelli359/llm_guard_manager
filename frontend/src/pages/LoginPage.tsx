import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Tabs } from 'antd';
import { UserOutlined, LockOutlined, SafetyCertificateOutlined, TeamOutlined } from '@ant-design/icons';
import api from '../api';

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [loginType, setLoginType] = useState('admin');

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('username', values.username);
      params.append('password', values.password);

      const response = await api.post('/login/access-token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const role = response.data.role;
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user_role', role);
      
      if (loginType === 'admin' && role !== 'ADMIN') {
          message.warning('您不是管理员，已跳转至审核界面');
      } else if (loginType === 'auditor' && role === 'ADMIN') {
          message.info('检测到管理员账号登录');
      }

      message.success('登录成功！');
      window.location.href = import.meta.env.BASE_URL || '/';
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码。');
    } finally {
      setLoading(false);
    }
  };

  const renderForm = () => (
    <Form
        name="normal_login"
        className="login-form"
        initialValues={{ remember: true }}
        onFinish={onFinish}
    >
        <Form.Item
        name="username"
        rules={[{ required: true, message: '请输入用户名！' }]}
        >
        <Input prefix={<UserOutlined className="site-form-item-icon" />} placeholder="用户名" size="large" />
        </Form.Item>
        <Form.Item
        name="password"
        rules={[{ required: true, message: '请输入密码！' }]}
        >
        <Input
            prefix={<LockOutlined className="site-form-item-icon" />}
            type="password"
            placeholder="密码"
            size="large"
        />
        </Form.Item>

        <Form.Item>
        <Button type="primary" htmlType="submit" className="login-form-button" loading={loading} block size="large">
            立即登录
        </Button>
        </Form.Item>
    </Form>
  );

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400, textAlign: 'center' }}>
        <h2 style={{ marginBottom: 24 }}>LLM Guard 管理平台</h2>
        <Tabs 
            activeKey={loginType} 
            onChange={setLoginType}
            centered
            items={[
                {
                    key: 'admin',
                    label: <span><SafetyCertificateOutlined />管理员登录</span>,
                    children: renderForm()
                },
                {
                    key: 'auditor',
                    label: <span><TeamOutlined />审核员登录</span>,
                    children: renderForm()
                }
            ]}
        />
      </Card>
    </div>
  );
};

export default LoginPage;
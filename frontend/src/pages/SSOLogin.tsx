import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spin, Result, Button } from 'antd';
import { ssoApi } from '../api';
import { usePermission } from '../hooks/usePermission';

/**
 * SSO登录页面
 *
 * 接收门户系统传递的Ticket，验证后完成登录
 * URL: /sso/login?ticket=TK_xxx&return_url=/dashboard
 */
const SSOLogin: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshPermissions } = usePermission();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    const ticket = searchParams.get('ticket');
    const returnUrl = searchParams.get('return_url') || '/';

    if (!ticket) {
      setStatus('error');
      setErrorMessage('缺少Ticket参数，请从门户系统登录');
      return;
    }

    // 使用Ticket登录
    const doLogin = async () => {
      try {
        const response = await ssoApi.login(ticket);
        const { access_token, role, user_id } = response.data;

        // 存储Token和用户信息
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user_role', role);
        localStorage.setItem('user_id', user_id);

        // 刷新权限信息
        await refreshPermissions();

        setStatus('success');

        // 延迟跳转，让用户看到成功提示
        setTimeout(() => {
          navigate(returnUrl, { replace: true });
        }, 500);

      } catch (error: any) {
        setStatus('error');
        const detail = error.response?.data?.detail || '登录失败，请重试';
        setErrorMessage(detail);
      }
    };

    doLogin();
  }, [searchParams, navigate]);

  // 返回门户系统
  const handleBackToPortal = () => {
    // TODO: 配置门户系统地址
    const portalUrl = import.meta.env.VITE_PORTAL_URL || '/login';
    window.location.href = portalUrl;
  };

  if (status === 'loading') {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <Spin size="large" />
        <span style={{ color: '#666' }}>正在登录，请稍候...</span>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <Result
          status="error"
          title="登录失败"
          subTitle={errorMessage}
          extra={[
            <Button type="primary" key="portal" onClick={handleBackToPortal}>
              返回门户系统
            </Button>,
            <Button key="retry" onClick={() => window.location.reload()}>
              重试
            </Button>
          ]}
        />
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh'
    }}>
      <Result
        status="success"
        title="登录成功"
        subTitle="正在跳转..."
      />
    </div>
  );
};

export default SSOLogin;

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { Layout, Menu, theme, Select } from 'antd';
import {
  TagsOutlined,
  GlobalOutlined,
  DashboardOutlined,
  AppstoreOutlined,
  LoginOutlined,
  SafetyCertificateOutlined,
  FileTextOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import MetaTagsPage from './pages/MetaTags';
import GlobalKeywordsPage from './pages/GlobalKeywords';
import GlobalPoliciesPage from './pages/GlobalPolicies';
import ScenarioKeywordsPage from './pages/ScenarioKeywords';
import ScenarioPoliciesPage from './pages/ScenarioPolicies';
import InputPlaygroundPage from './pages/InputPlayground';
import AppsPage from './pages/Apps';
import AppDashboard from './pages/AppDashboard';
import LoginPage from './pages/LoginPage';
import { scenariosApi } from './api';
import { ScenarioApp } from './types';

// Placeholder components
const Dashboard = () => <div><h2>欢迎使用 LLM Guard 管理平台</h2><p>请从左侧菜单选择应用进行管理，或前往“应用管理”创建新应用。</p></div>;

const { Header, Content, Footer, Sider } = Layout;

// Protected Route Component
const AuthLayout: React.FC = () => {
  const isAuthenticated = localStorage.getItem('access_token');
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
};


const AppLayout: React.FC = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const location = useLocation();
  const navigate = useNavigate();

  const [apps, setApps] = useState<ScenarioApp[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<string | null>(localStorage.getItem('current_app_id'));

  useEffect(() => {
    fetchApps();
  }, []);

  const fetchApps = async () => {
    try {
        const res = await scenariosApi.getAll();
        setApps(res.data);
        // If current selected app is not in the list (e.g. deleted), clear it
        if (selectedAppId && !res.data.find(app => app.app_id === selectedAppId)) {
            setSelectedAppId(null);
            localStorage.removeItem('current_app_id');
        }
    } catch (error) {
        console.error("Failed to fetch apps", error);
    }
  };

  const handleAppChange = (value: string) => {
    setSelectedAppId(value);
    localStorage.setItem('current_app_id', value);
    // Optionally auto-navigate to dashboard when switching app
    navigate(`/apps/${value}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_app_id');
    navigate('/login');
  };

  // Construct Menu Items
  const menuItems: any[] = [
    {
      type: 'group',
      label: '全局配置',
      children: [
        {
            key: '/apps',
            icon: <AppstoreOutlined />,
            label: <Link to="/apps">应用管理</Link>,
        },
        {
            key: '/tags',
            icon: <TagsOutlined />,
            label: <Link to="/tags">标签管理</Link>,
        },
        {
            key: '/global-keywords',
            icon: <GlobalOutlined />,
            label: <Link to="/global-keywords">全局敏感词</Link>,
        },
        {
            key: '/global-policies',
            icon: <SafetyCertificateOutlined />,
            label: <Link to="/global-policies">全局默认规则</Link>,
        },
      ]
    },
    {
      type: 'group',
      label: '测试工具',
      children: [
        {
          key: '/playground',
          icon: <ExperimentOutlined />,
          label: <Link to="/playground">输入试验场</Link>,
        },
      ]
    }
  ];

  if (selectedAppId) {
      menuItems.push({
          type: 'divider'
      });
      menuItems.push({
          type: 'group',
          label: `当前应用: ${selectedAppId}`,
          children: [
            {
                key: `/apps/${selectedAppId}`,
                icon: <DashboardOutlined />,
                label: <Link to={`/apps/${selectedAppId}`}>应用概览</Link>,
            },
            {
                key: `/apps/${selectedAppId}/policies`,
                icon: <SafetyCertificateOutlined />,
                label: <Link to={`/apps/${selectedAppId}/policies`}>场景策略管理</Link>,
            },
          ]
      });
  }
  
  // Append Logout at the end
  menuItems.push({ type: 'divider' });
  menuItems.push({
      key: '/logout',
      icon: <LoginOutlined />,
      label: '退出登录',
      onClick: handleLogout,
      danger: true
  });

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
      >
        <div style={{ padding: '16px', color: 'white', fontWeight: 'bold', fontSize: '18px', textAlign: 'center' }}>
            LLM Guard 管理平台
        </div>
        
        <div style={{ padding: '0 16px 16px 16px' }}>
            <Select
                style={{ width: '100%' }}
                placeholder="请选择应用..."
                value={selectedAppId}
                onChange={handleAppChange}
                options={apps.map(app => ({ label: app.app_name, value: app.app_id }))}
                loading={apps.length === 0}
                notFoundContent="未找到应用"
            />
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }} />
        <Content style={{ margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            <Routes>
              {/* Nested routes for AppLayout, rendered via Outlet in AuthLayout */}
              <Route path="/" element={<Dashboard />} />
              <Route path="/apps" element={<AppsPage />} />
              
              {/* App Specific Routes */}
              <Route path="/apps/:appId" element={<AppDashboard />} />
              <Route path="/apps/:appId/keywords" element={<ScenarioKeywordsPage />} />
              <Route path="/apps/:appId/policies" element={<ScenarioPoliciesPage />} />
              
              <Route path="/tags" element={<MetaTagsPage />} />
              <Route path="/global-keywords" element={<GlobalKeywordsPage />} />
              <Route path="/global-policies" element={<GlobalPoliciesPage />} />
              <Route path="/playground" element={<InputPlaygroundPage />} />
            </Routes>
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          LLM Guard Manager ©{new Date().getFullYear()} Created by Corelli
        </Footer>
      </Layout>
    </Layout>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AuthLayout />}>
          <Route path="/*" element={<AppLayout />} /> {/* Catch all other routes under AuthLayout */}
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
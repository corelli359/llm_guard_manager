import React, { useState, useEffect, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import type { MenuProps } from 'antd';
import {
  ExperimentOutlined,
  AppstoreOutlined,
  TagsOutlined,
  GlobalOutlined,
  SafetyCertificateOutlined,
  DashboardOutlined,
  LoginOutlined,
  ThunderboltOutlined,
  UserOutlined,
  AuditOutlined,
  BarChartOutlined,
  FileTextOutlined,
  TeamOutlined
} from '@ant-design/icons';
import MetaTagsPage from './pages/MetaTags';
import GlobalKeywordsPage from './pages/GlobalKeywords';
import GlobalPoliciesPage from './pages/GlobalPolicies';
import ScenarioKeywordsPage from './pages/ScenarioKeywords';
import ScenarioPoliciesPage from './pages/ScenarioPolicies';
import InputPlaygroundPage from './pages/InputPlayground';
import PerformanceTestPage from './pages/PerformanceTest';
import UsersPage from './pages/UsersPage';
import SmartLabelingPage from './pages/SmartLabeling';
import AnnotatorStatsPage from './pages/AnnotatorStats';
import AppsPage from './pages/Apps';
import AppDashboard from './pages/AppDashboard';
import LoginPage from './pages/LoginPage';
import SSOLogin from './pages/SSOLogin';
import AuditLogsPage from './pages/AuditLogs';
import MyScenariosPage from './pages/MyScenarios';
import RolesPage from './pages/RolesPage';
import { scenariosApi } from './api';
import { PermissionProvider } from './contexts/PermissionContext';
import { usePermission } from './hooks/usePermission';

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
  const { userRole, userPermissions, hasRole, hasPermission } = usePermission();

  const [selectedAppId, setSelectedAppId] = useState<string | null>(localStorage.getItem('current_app_id'));

  useEffect(() => {
    fetchApps();
  }, []);

  const fetchApps = async () => {
    try {
        const res = await scenariosApi.getAll();
        // If current selected app is not in the list (e.g. deleted), clear it
        if (selectedAppId && !res.data.find(app => app.app_id === selectedAppId)) {
            setSelectedAppId(null);
            localStorage.removeItem('current_app_id');
        }
    } catch (error) {
        console.error("Failed to fetch apps", error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_app_id');
    localStorage.removeItem('user_role');
    navigate('/login');
  };

  // Construct Menu Items based on permissions
  const menuItems: MenuProps['items'] = useMemo(() => {
    const items: MenuProps['items'] = [];

    if (hasPermission('smart_labeling')) {
      items.push({
        key: '/smart-labeling',
        icon: <AuditOutlined />,
        label: <Link to="/smart-labeling">智能标注</Link>,
      });
    }

    if (hasPermission('annotator_stats')) {
      items.push({
        key: '/annotator-stats',
        icon: <BarChartOutlined />,
        label: <Link to="/annotator-stats">标注统计</Link>,
      });
    }

    const systemChildren: any[] = [];
    if (hasPermission('user_management')) {
      systemChildren.push({
        key: '/users',
        icon: <UserOutlined />,
        label: <Link to="/users">用户管理</Link>,
      });
    }
    if (hasPermission('role_management')) {
      systemChildren.push({
        key: '/roles',
        icon: <TeamOutlined />,
        label: <Link to="/roles">角色管理</Link>,
      });
    }
    if (hasPermission('audit_logs')) {
      systemChildren.push({
        key: '/audit-logs',
        icon: <FileTextOutlined />,
        label: <Link to="/audit-logs">审计日志</Link>,
      });
    }
    if (systemChildren.length > 0) {
      items.push({ type: 'group', label: '系统管理', children: systemChildren });
    }

    const globalChildren: any[] = [];
    if (hasPermission('app_management')) {
      globalChildren.push({
        key: '/apps',
        icon: <AppstoreOutlined />,
        label: <Link to="/apps">应用管理</Link>,
      });
    }
    if (hasPermission('tag_management')) {
      globalChildren.push({
        key: '/tags',
        icon: <TagsOutlined />,
        label: <Link to="/tags">标签管理</Link>,
      });
    }
    if (hasPermission('global_keywords')) {
      globalChildren.push({
        key: '/global-keywords',
        icon: <GlobalOutlined />,
        label: <Link to="/global-keywords">全局敏感词</Link>,
      });
    }
    if (hasPermission('global_policies')) {
      globalChildren.push({
        key: '/global-policies',
        icon: <SafetyCertificateOutlined />,
        label: <Link to="/global-policies">全局默认规则</Link>,
      });
    }
    if (globalChildren.length > 0) {
      items.push({ type: 'group', label: '全局配置', children: globalChildren });
    }

    const toolChildren: any[] = [];
    if (hasPermission('playground')) {
      toolChildren.push({
        key: '/playground',
        icon: <ExperimentOutlined />,
        label: <Link to="/playground">输入试验场</Link>,
      });
    }
    if (hasPermission('performance_test')) {
      toolChildren.push({
        key: '/performance',
        icon: <ThunderboltOutlined />,
        label: <Link to="/performance">性能测试</Link>,
      });
    }
    if (toolChildren.length > 0) {
      items.push({ type: 'group', label: '测试工具', children: toolChildren });
    }

    if (hasRole(['SCENARIO_ADMIN', 'ANNOTATOR'])) {
      const myScenarios = userPermissions?.scenario_permissions
        ? Object.keys(userPermissions.scenario_permissions)
        : [];
      if (myScenarios.length > 0) {
        items.push({ type: 'divider' });
        items.push({
          key: '/my-scenarios',
          icon: <AppstoreOutlined />,
          label: <Link to="/my-scenarios">我的场景</Link>,
        });
      }
    }

    if (selectedAppId && hasPermission('app_management')) {
      items.push({ type: 'divider' });
      items.push({
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
        ],
      });
    }

    items.push({ type: 'divider' });
    items.push({
      key: '/logout',
      icon: <LoginOutlined />,
      label: '退出登录',
      onClick: handleLogout,
      danger: true,
    });

    return items;
  }, [userRole, userPermissions, selectedAppId, hasRole, hasPermission]);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
      >
        <div style={{ padding: '16px', color: 'white', fontWeight: 'bold', fontSize: '18px', textAlign: 'center' }}>
            LLM Guard 管理平台
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
              <Route path="/performance" element={<PerformanceTestPage />} />
              <Route path="/users" element={<UsersPage />} />
              <Route path="/roles" element={<RolesPage />} />
              <Route path="/smart-labeling" element={<SmartLabelingPage />} />
              <Route path="/annotator-stats" element={<AnnotatorStatsPage />} />
              <Route path="/audit-logs" element={<AuditLogsPage />} />
              <Route path="/my-scenarios" element={<MyScenariosPage />} />
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
    <PermissionProvider>
      <Router basename={import.meta.env.BASE_URL}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/sso/login" element={<SSOLogin />} />
          <Route element={<AuthLayout />}>
            <Route path="/*" element={<AppLayout />} /> {/* Catch all other routes under AuthLayout */}
          </Route>
        </Routes>
      </Router>
    </PermissionProvider>
  );
};

export default App;
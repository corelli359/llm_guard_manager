import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import {
  TagsOutlined,
  GlobalOutlined,
  DashboardOutlined,
  AppstoreOutlined
} from '@ant-design/icons';
import MetaTagsPage from './pages/MetaTags';
import GlobalKeywordsPage from './pages/GlobalKeywords';
import ScenarioKeywordsPage from './pages/ScenarioKeywords';
import ScenarioPoliciesPage from './pages/ScenarioPolicies';
import AppsPage from './pages/Apps';
import AppDashboard from './pages/AppDashboard';

// Placeholder components
const Dashboard = () => <div><h2>Welcome to LLM Guard Manager</h2><p>Select a module from the sidebar to manage configurations.</p></div>;

const { Header, Content, Footer, Sider } = Layout;

const AppLayout: React.FC = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: '/apps',
      icon: <AppstoreOutlined />,
      label: <Link to="/apps">App Management</Link>,
    },
    {
      key: '/tags',
      icon: <TagsOutlined />,
      label: <Link to="/tags">Meta Tags</Link>,
    },
    {
      key: '/global-keywords',
      icon: <GlobalOutlined />,
      label: <Link to="/global-keywords">Global Keywords</Link>,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div className="demo-logo-vertical" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)' }} />
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
              <Route path="/" element={<Dashboard />} />
              <Route path="/apps" element={<AppsPage />} />
              <Route path="/apps/:appId" element={<AppDashboard />} />
              <Route path="/apps/:appId/keywords" element={<ScenarioKeywordsPage />} />
              <Route path="/apps/:appId/policies" element={<ScenarioPoliciesPage />} />
              
              <Route path="/tags" element={<MetaTagsPage />} />
              <Route path="/global-keywords" element={<GlobalKeywordsPage />} />
              <Route path="/scenario-keywords" element={<ScenarioKeywordsPage />} />
              <Route path="/scenario-policies" element={<ScenarioPoliciesPage />} />
            </Routes>
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          LLM Guard Manager ©{new Date().getFullYear()}
        </Footer>
      </Layout>
    </Layout>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
};

export default App;

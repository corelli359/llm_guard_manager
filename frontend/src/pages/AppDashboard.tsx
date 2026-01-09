import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Descriptions, Badge, Button, Row, Col, Spin, Tag, message } from 'antd';
import { SafetyCertificateOutlined, AlertOutlined, CheckCircleOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { scenariosApi } from '../api';
import { ScenarioApp } from '../types';

const AppDashboard: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const [appData, setAppData] = useState<ScenarioApp | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (appId) {
      fetchApp(appId);
    }
  }, [appId]);

  const fetchApp = async (id: string) => {
    try {
      const res = await scenariosApi.getByAppId(id);
      setAppData(res.data);
    } catch (error) {
      message.error('App not found');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spin size="large" />;
  if (!appData) return <div>App not found</div>;

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} style={{ marginBottom: 16 }} onClick={() => window.history.back()}>
        Back to Apps
      </Button>

      <Card title={appData.app_name} extra={<Badge status={appData.is_active ? "success" : "default"} text={appData.is_active ? "Active" : "Inactive"} />}>
        <Descriptions bordered>
          <Descriptions.Item label="App ID">{appData.app_id}</Descriptions.Item>
          <Descriptions.Item label="Description" span={2}>{appData.description || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <h3 style={{ marginTop: 24 }}>Enabled Features & Configuration</h3>
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card 
            title="Blacklist Keywords" 
            actions={[<Link to={`/apps/${appData.app_id}/keywords?category=1`}>Manage Blacklist</Link>]}
          >
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <AlertOutlined style={{ fontSize: 32, color: appData.enable_blacklist ? '#ff4d4f' : '#d9d9d9' }} />
            </div>
            <div style={{ textAlign: 'center' }}>
                Status: {appData.enable_blacklist ? <Tag color="green">Enabled</Tag> : <Tag>Disabled</Tag>}
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card 
            title="Whitelist Keywords" 
            actions={[<Link to={`/apps/${appData.app_id}/keywords?category=0`}>Manage Whitelist</Link>]}
          >
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <CheckCircleOutlined style={{ fontSize: 32, color: appData.enable_whitelist ? '#52c41a' : '#d9d9d9' }} />
            </div>
            <div style={{ textAlign: 'center' }}>
                Status: {appData.enable_whitelist ? <Tag color="green">Enabled</Tag> : <Tag>Disabled</Tag>}
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card 
            title="Custom Policies" 
            actions={[<Link to={`/apps/${appData.app_id}/policies`}>Manage Policies</Link>]}
          >
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <SafetyCertificateOutlined style={{ fontSize: 32, color: appData.enable_custom_policy ? '#1890ff' : '#d9d9d9' }} />
            </div>
            <div style={{ textAlign: 'center' }}>
                Status: {appData.enable_custom_policy ? <Tag color="green">Enabled</Tag> : <Tag>Disabled</Tag>}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AppDashboard;

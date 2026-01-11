import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Badge, Button, Row, Col, Spin, Tag, message } from 'antd';
import { SafetyCertificateOutlined, AlertOutlined, CheckCircleOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { scenariosApi } from '../api';
import { ScenarioApp } from '../types';

const AppDashboard: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const navigate = useNavigate();
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
      message.error('未找到该应用');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '50px auto' }} />;
  if (!appData) return <div>应用未找到</div>;

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} style={{ marginBottom: 16 }} onClick={() => navigate('/apps')}>
        返回应用列表
      </Button>

      <Card 
        title={`应用详情: ${appData.app_name}`} 
        extra={<Badge status={appData.is_active ? "success" : "default"} text={appData.is_active ? "运行中" : "已停用"} />}
      >
        <Descriptions bordered>
          <Descriptions.Item label="应用 ID (App ID)">{appData.app_id}</Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>{appData.description || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      <h3 style={{ marginTop: 24 }}>功能模块配置</h3>
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card 
            title="敏感词黑名单" 
            actions={[<Link to={`/apps/${appData.app_id}/keywords?category=1`}>管理黑名单</Link>]}
          >
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <AlertOutlined style={{ fontSize: 32, color: appData.enable_blacklist ? '#ff4d4f' : '#d9d9d9' }} />
            </div>
            <div style={{ textAlign: 'center' }}>
                状态: {appData.enable_blacklist ? <Tag color="green">已启用</Tag> : <Tag>未启用</Tag>}
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card 
            title="敏感词白名单" 
            actions={[<Link to={`/apps/${appData.app_id}/keywords?category=0`}>管理白名单</Link>]}
          >
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <CheckCircleOutlined style={{ fontSize: 32, color: appData.enable_whitelist ? '#52c41a' : '#d9d9d9' }} />
            </div>
            <div style={{ textAlign: 'center' }}>
                状态: {appData.enable_whitelist ? <Tag color="green">已启用</Tag> : <Tag>未启用</Tag>}
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card 
            title="自定义处置策略" 
            actions={[<Link to={`/apps/${appData.app_id}/policies`}>管理策略规则</Link>]}
          >
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <SafetyCertificateOutlined style={{ fontSize: 32, color: appData.enable_custom_policy ? '#1890ff' : '#d9d9d9' }} />
            </div>
            <div style={{ textAlign: 'center' }}>
                状态: {appData.enable_custom_policy ? <Tag color="green">已启用</Tag> : <Tag>未启用</Tag>}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AppDashboard;
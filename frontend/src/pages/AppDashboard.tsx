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
        <Col span={24}>
          <Card 
            title="场景策略配置" 
            extra={<Link to={`/apps/${appData.app_id}/policies`}><Button type="primary">进入配置</Button></Link>}
          >
            <Row gutter={16} style={{ textAlign: 'center' }}>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>
                   <AlertOutlined style={{ fontSize: 24, color: appData.enable_blacklist ? '#ff4d4f' : '#d9d9d9' }} />
                   <div style={{ marginTop: 8 }}>敏感词黑名单</div>
                </div>
                <Tag color={appData.enable_blacklist ? "green" : "default"}>{appData.enable_blacklist ? "已启用" : "未启用"}</Tag>
              </Col>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>
                   <CheckCircleOutlined style={{ fontSize: 24, color: appData.enable_whitelist ? '#52c41a' : '#d9d9d9' }} />
                   <div style={{ marginTop: 8 }}>敏感词白名单</div>
                </div>
                <Tag color={appData.enable_whitelist ? "green" : "default"}>{appData.enable_whitelist ? "已启用" : "未启用"}</Tag>
              </Col>
              <Col span={8}>
                <div style={{ marginBottom: 8 }}>
                   <SafetyCertificateOutlined style={{ fontSize: 24, color: appData.enable_custom_policy ? '#1890ff' : '#d9d9d9' }} />
                   <div style={{ marginTop: 8 }}>自定义规则</div>
                </div>
                <Tag color={appData.enable_custom_policy ? "green" : "default"}>{appData.enable_custom_policy ? "已启用" : "未启用"}</Tag>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AppDashboard;
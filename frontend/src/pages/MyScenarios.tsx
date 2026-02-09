import React from 'react';
import { Card, List, Tag, Space, Button, Empty, Spin } from 'antd';
import { AppstoreOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { usePermission } from '../hooks/usePermission';

const PERMISSION_LABELS: Record<string, string> = {
  scenario_keywords: '敏感词管理',
  scenario_policies: '策略管理',
  scenario_playground: '测试工具',
  scenario_performance: '性能测试',
  scenario_basic_info: '基本信息',
};

const MyScenarios: React.FC = () => {
  const navigate = useNavigate();
  const { userPermissions, loading } = usePermission();

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  const scenarioEntries = userPermissions?.scenario_permissions
    ? Object.entries(userPermissions.scenario_permissions)
    : [];

  if (scenarioEntries.length === 0) {
    return (
      <Card title="我的场景">
        <Empty description="您还没有被分配任何场景" />
      </Card>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <Card title="我的场景" extra={<Tag color="blue">{scenarioEntries.length} 个场景</Tag>}>
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 }}
          dataSource={scenarioEntries}
          renderItem={([scenarioId, permissions]) => (
            <List.Item>
              <Card
                hoverable
                onClick={() => navigate(`/apps/${scenarioId}`)}
                style={{ height: '100%' }}
              >
                <div style={{ marginBottom: 16 }}>
                  <Space>
                    <AppstoreOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                    <div style={{ fontWeight: 'bold', fontSize: 16 }}>
                      {scenarioId}
                    </div>
                  </Space>
                </div>

                {permissions.length > 0 && (
                  <div>
                    <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>权限:</div>
                    <Space wrap size={[0, 8]}>
                      {permissions.map((perm) => (
                        <Tag key={perm} icon={<CheckCircleOutlined />} color="success">
                          {PERMISSION_LABELS[perm] || perm}
                        </Tag>
                      ))}
                    </Space>
                  </div>
                )}

                <div style={{ marginTop: 16, textAlign: 'right' }}>
                  <Button type="link" size="small">进入管理 →</Button>
                </div>
              </Card>
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default MyScenarios;

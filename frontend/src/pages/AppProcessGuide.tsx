import React from 'react';
import { Card, Tag, Button } from 'antd';
import {
  FormOutlined,
  AuditOutlined,
  AppstoreAddOutlined,
  KeyOutlined,
  SafetyCertificateOutlined,
  RocketOutlined,
  ArrowRightOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

interface StepNode {
  icon: React.ReactNode;
  title: string;
  description: string;
  role: string;
  roleColor: string;
}

const steps: StepNode[] = [
  {
    icon: <FormOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
    title: '提交接入申请',
    description: '业务方填写应用信息，提交接入安全围栏的申请',
    role: '业务方',
    roleColor: 'blue',
  },
  {
    icon: <AuditOutlined style={{ fontSize: 32, color: '#faad14' }} />,
    title: '管理员审批',
    description: '平台管理员审核申请，确认应用合规性与接入必要性',
    role: '管理员',
    roleColor: 'orange',
  },
  {
    icon: <AppstoreAddOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
    title: '应用注册',
    description: '审批通过后，管理员在平台注册应用并分配唯一 App ID',
    role: '管理员',
    roleColor: 'orange',
  },
  {
    icon: <KeyOutlined style={{ fontSize: 32, color: '#722ed1' }} />,
    title: '分配场景权限',
    description: '为业务方场景管理员分配该应用的管理权限，包括词库和策略配置',
    role: '管理员',
    roleColor: 'orange',
  },
  {
    icon: <SafetyCertificateOutlined style={{ fontSize: 32, color: '#eb2f96' }} />,
    title: '配置安全策略',
    description: '业务方场景管理员配置敏感词黑白名单、处置策略，并在试验场验证',
    role: '业务方场景管理员',
    roleColor: 'blue',
  },
  {
    icon: <RocketOutlined style={{ fontSize: 32, color: '#13c2c2' }} />,
    title: '上线运行',
    description: '业务方对接 API 接口，应用正式接入安全围栏服务',
    role: '业务方',
    roleColor: 'blue',
  },
];

const AppProcessGuide: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>应用接入与权限申请流程</h2>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/apps')}>
          返回场景管理
        </Button>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 8,
        overflowX: 'auto',
        padding: '16px 0',
      }}>
        {steps.map((step, index) => (
          <React.Fragment key={index}>
            <Card
              hoverable
              style={{
                width: 200,
                minWidth: 200,
                textAlign: 'center',
                borderTop: '3px solid #1890ff',
              }}
              styles={{ body: { padding: '20px 16px' } }}
            >
              <div style={{ marginBottom: 12 }}>{step.icon}</div>
              <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 8 }}>{step.title}</div>
              <div style={{ color: '#666', fontSize: 13, marginBottom: 12, minHeight: 60 }}>
                {step.description}
              </div>
              <Tag color={step.roleColor}>{step.role}</Tag>
            </Card>
            {index < steps.length - 1 && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                paddingTop: 60,
                color: '#bbb',
                fontSize: 20,
              }}>
                <ArrowRightOutlined />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      <Card style={{ marginTop: 32 }} title="说明">
        <ul style={{ lineHeight: 2, color: '#555' }}>
          <li>新应用接入需由<b>管理员</b>在"场景管理"页面完成注册</li>
          <li>注册后，管理员可在"用户管理"中为<b>业务方场景管理员</b>分配对应应用的权限</li>
          <li>业务方场景管理员登录后，可在"我的场景"中管理被授权应用的敏感词和策略</li>
          <li>配置完成后，建议在"输入试验场"中验证策略效果，确认无误后通知业务方对接</li>
        </ul>
      </Card>
    </div>
  );
};

export default AppProcessGuide;

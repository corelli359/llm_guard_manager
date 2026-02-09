import React, { useState, useEffect } from 'react';
import { Tabs, Button, Card, Row, Col, Input, message, Result } from 'antd';
import { SearchOutlined, ArrowLeftOutlined, LockOutlined } from '@ant-design/icons';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import ScenarioKeywordsTab from '../components/ScenarioKeywordsTab';
import ScenarioRulesTab from '../components/ScenarioRulesTab';
import { usePermission } from '../hooks/usePermission';

const { TabPane } = Tabs;

const ScenarioPoliciesPage: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { hasPermission, hasScenarioPermission } = usePermission();

  const [currentScenarioId, setCurrentScenarioId] = useState<string>('');
  const [searchScenarioId, setSearchScenarioId] = useState<string>('');
  const [activeMode, setActiveMode] = useState<'custom' | 'super'>('custom');
  const [activeTab, setActiveTab] = useState<string>('keywords');

  // Initial load from URL
  useEffect(() => {
    if (appId) {
      setCurrentScenarioId(appId);
      setSearchScenarioId(appId);
    }

    const modeParam = searchParams.get('mode');
    if (modeParam === 'custom' || modeParam === 'super') {
      setActiveMode(modeParam);
    }

    const tabParam = searchParams.get('tab');
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [appId, searchParams]);

  const handleSearch = () => {
    if (searchScenarioId.trim()) {
      setCurrentScenarioId(searchScenarioId.trim());
    } else {
      message.warning('请输入场景 ID');
    }
  };

  // 权限检查：全局权限或场景级权限
  const canKeywords = currentScenarioId
    ? hasPermission('scenario_keywords') || hasScenarioPermission(currentScenarioId, 'scenario_keywords')
    : false;
  const canPolicies = currentScenarioId
    ? hasPermission('scenario_policies') || hasScenarioPermission(currentScenarioId, 'scenario_policies')
    : false;
  const hasAnyAccess = canKeywords || canPolicies;

  // 默认选中有权限的 tab
  useEffect(() => {
    if (currentScenarioId && !searchParams.get('tab')) {
      if (canKeywords) setActiveTab('keywords');
      else if (canPolicies) setActiveTab('rules');
    }
  }, [currentScenarioId, canKeywords, canPolicies]);

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        {appId && (
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/apps/${appId}`)} style={{ marginBottom: 16 }}>
            返回应用概览
          </Button>
        )}
        <h2>场景策略管理 {appId ? `- ${appId}` : ''}</h2>

        {!appId && (
          <Card title="选择场景" style={{ marginBottom: 16 }}>
            <Row gutter={16} align="middle">
              <Col>
                <span>场景 ID (Scenario ID): </span>
              </Col>
              <Col flex="auto">
                <Input
                  placeholder="请输入场景 ID"
                  value={searchScenarioId}
                  onChange={e => setSearchScenarioId(e.target.value)}
                  onPressEnter={handleSearch}
                />
              </Col>
              <Col>
                <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                  加载策略
                </Button>
              </Col>
            </Row>
          </Card>
        )}
      </div>

      {currentScenarioId && !hasAnyAccess && (
        <Result
          icon={<LockOutlined />}
          title="权限不足"
          subTitle="您没有该场景的敏感词管理或策略管理权限"
          extra={appId && (
            <Button type="primary" onClick={() => navigate(-1)}>返回</Button>
          )}
        />
      )}

      {currentScenarioId && hasAnyAccess && (
        <Tabs
          activeKey={activeMode}
          onChange={(key) => setActiveMode(key as 'custom' | 'super')}
          type="card"
        >
          <TabPane tab="自定义模式管理" key="custom">
            <Tabs activeKey={activeTab} onChange={setActiveTab} type="line">
              {canKeywords && (
                <TabPane tab="敏感词管理（黑名单/白名单）" key="keywords">
                  <ScenarioKeywordsTab scenarioId={currentScenarioId} mode="custom" />
                </TabPane>
              )}
              {canPolicies && (
                <TabPane tab="规则管理" key="rules">
                  <ScenarioRulesTab scenarioId={currentScenarioId} ruleMode={1} modeName="自定义模式" />
                </TabPane>
              )}
            </Tabs>
          </TabPane>

          <TabPane tab="超级模式管理" key="super">
            <Tabs activeKey={activeTab} onChange={setActiveTab} type="line">
              {canKeywords && (
                <TabPane tab="敏感词管理（黑名单/白名单）" key="keywords">
                  <ScenarioKeywordsTab scenarioId={currentScenarioId} mode="super" />
                </TabPane>
              )}
              {canPolicies && (
                <TabPane tab="规则管理" key="rules">
                  <ScenarioRulesTab scenarioId={currentScenarioId} ruleMode={0} modeName="超级模式" />
                </TabPane>
              )}
            </Tabs>
          </TabPane>
        </Tabs>
      )}
    </div>
  );
};

export default ScenarioPoliciesPage;

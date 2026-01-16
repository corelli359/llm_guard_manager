import React, { useState, useEffect } from 'react';
import { Table, Button, Tabs, Tag, Space, message, Select, Radio, Tooltip, Alert, Popconfirm } from 'antd';
import { CheckOutlined, CloseOutlined, CloudUploadOutlined, UserOutlined, DeleteOutlined } from '@ant-design/icons';
import { stagingApi } from '../api';
import dayjs from 'dayjs';

const { TabPane } = Tabs;
const { Option } = Select;

const SmartLabelingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('keywords');
  const [data, setData] = useState([]);
  const [rulesData, setRulesData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [syncing, setSyncing] = useState(false);
  
  // Static options
  const tagOptions = ['POLITICAL', 'PORN', 'AD', 'VIOLENCE', 'OTHER'];
  const riskOptions = ['High', 'Medium', 'Low'];
  const strategyOptions = ['BLOCK', 'PASS', 'REWRITE'];

  const userRole = localStorage.getItem('user_role');
  const isAdmin = userRole === 'ADMIN';

  useEffect(() => {
    fetchData();
  }, [activeTab, statusFilter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'keywords') {
          const res = await stagingApi.listKeywords(statusFilter);
          setData(res.data);
      } else {
          const res = await stagingApi.listRules(statusFilter);
          setRulesData(res.data);
      }
    } catch (e) {
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  // --- Keyword Logic ---
  const handleReviewKeyword = async (record: any, newStatus: string, changes: any = {}) => {
    try {
      await stagingApi.reviewKeyword(record.id, {
        final_tag: changes.final_tag || record.final_tag || record.predicted_tag,
        final_risk: changes.final_risk || record.final_risk || record.predicted_risk,
        status: newStatus
      });
      message.success('操作成功');
      fetchData();
    } catch (e) {
      message.error('操作失败');
    }
  };

  const handleDeleteKeyword = async (id: string) => {
      try {
          await stagingApi.deleteKeyword(id);
          message.success('已删除');
          fetchData();
      } catch (e) {
          message.error('删除失败');
      }
  };

  // --- Rule Logic ---
  const handleReviewRule = async (record: any, newStatus: string, changes: any = {}) => {
    try {
      await stagingApi.reviewRule(record.id, {
        final_strategy: changes.final_strategy || record.final_strategy || record.predicted_strategy,
        status: newStatus
      });
      message.success('操作成功');
      fetchData();
    } catch (e) {
      message.error('操作失败');
    }
  };

  const handleDeleteRule = async (id: string) => {
      try {
          await stagingApi.deleteRule(id);
          message.success('已删除');
          fetchData();
      } catch (e) {
          message.error('删除失败');
      }
  };

  // --- Sync Logic ---
  const handleSync = async () => {
    if (selectedRowKeys.length === 0) return;
    setSyncing(true);
    try {
      let res;
      if (activeTab === 'keywords') {
          res = await stagingApi.syncKeywords(selectedRowKeys as string[]);
      } else {
          res = await stagingApi.syncRules(selectedRowKeys as string[]);
      }
      message.success(`成功同步 ${res.data.synced_count} 条数据入库`);
      setSelectedRowKeys([]);
      fetchData();
    } catch (e) {
      message.error('同步失败');
    } finally {
      setSyncing(false);
    }
  };

  const handleImportMock = async () => {
      if (activeTab === 'keywords') {
          await stagingApi.importMock();
      } else {
          await stagingApi.importMockRules();
      }
      fetchData();
      message.success('Mock 数据已导入');
  };

  // --- UI Helpers ---
  const renderHelpMessage = () => (
      <Alert
        message="操作指引"
        description={
            <ul style={{ paddingLeft: 20, margin: 0 }}>
                <li><strong>确认 (Confirm) <CheckOutlined /></strong>: 认可模型结果或已修正数据，标记为“已审核 (Reviewed)”。管理员可将其同步入库。</li>
                <li><strong>忽略 (Ignore) <CloseOutlined /></strong>: 认为数据无效，标记为“已忽略 (Ignored)”。忽略的数据不会入库，后续可删除。</li>
                <li><strong>入库 (Sync) <CloudUploadOutlined /></strong>: (仅管理员) 批量将“已审核”的数据写入正式环境。</li>
            </ul>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
  );

  // --- Columns ---
  const statusColumn = {
        title: '状态',
        key: 'status',
        render: (_: any, record: any) => (
            <Space direction="vertical" size={0}>
                <Tag color={record.status === 'PENDING' ? 'blue' : record.status === 'REVIEWED' ? 'green' : record.status === 'SYNCED' ? 'purple' : 'default'}>
                    {record.status}
                </Tag>
                {record.is_modified && <Tag color="warning">Modified</Tag>}
            </Space>
        )
  };

  const auditColumn = {
        title: '审计信息',
        key: 'audit',
        render: (_: any, record: any) => record.annotator ? (
            <Tooltip title={dayjs(record.annotated_at).format('YYYY-MM-DD HH:mm')}>
                <Tag icon={<UserOutlined />}>{record.annotator}</Tag>
            </Tooltip>
        ) : '-'
  };

  const keywordColumns = [
    { title: '敏感词', dataIndex: 'keyword', key: 'keyword' },
    {
        title: '模型预测',
        key: 'prediction',
        render: (_: any, record: any) => (
            <Space direction="vertical" size={0}>
                <Tag>{record.predicted_tag}</Tag>
                <Tag color="orange" style={{fontSize: 10}}>{record.predicted_risk}</Tag>
            </Space>
        )
    },
    {
        title: '人工修正 (Final)',
        key: 'final',
        render: (_: any, record: any) => {
            const isEditable = record.status !== 'SYNCED';
            return (
                <Space direction="vertical" size={4}>
                    <Select 
                        defaultValue={record.final_tag || record.predicted_tag} 
                        style={{ width: 120 }} size="small" disabled={!isEditable}
                        onChange={(val) => handleReviewKeyword(record, 'REVIEWED', { final_tag: val })}
                    >
                        {tagOptions.map(t => <Option key={t} value={t}>{t}</Option>)}
                    </Select>
                    <Select 
                        defaultValue={record.final_risk || record.predicted_risk} 
                        style={{ width: 120 }} size="small" disabled={!isEditable}
                        onChange={(val) => handleReviewKeyword(record, 'REVIEWED', { final_risk: val })}
                    >
                        {riskOptions.map(r => <Option key={r} value={r}>{r}</Option>)}
                    </Select>
                </Space>
            );
        }
    },
    statusColumn,
    auditColumn,
    {
        title: '操作',
        key: 'action',
        render: (_: any, record: any) => (
            <Space>
                {record.status === 'PENDING' && (
                    <Tooltip title="确认通过">
                        <Button type="primary" size="small" icon={<CheckOutlined />} onClick={() => handleReviewKeyword(record, 'REVIEWED')} />
                    </Tooltip>
                )}
                {record.status !== 'IGNORED' && record.status !== 'SYNCED' && (
                    <Tooltip title="忽略">
                        <Button size="small" danger icon={<CloseOutlined />} onClick={() => handleReviewKeyword(record, 'IGNORED')} />
                    </Tooltip>
                )}
                {record.status === 'IGNORED' && (
                    <Popconfirm title="确定彻底删除?" onConfirm={() => handleDeleteKeyword(record.id)}>
                        <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
                    </Popconfirm>
                )}
            </Space>
        )
    }
  ];

  const rulesColumns = [
    { title: '标签', dataIndex: 'tag_code', key: 'tag_code', render: (t: string) => <Tag color="blue">{t}</Tag> },
    { title: '额外条件', dataIndex: 'extra_condition', key: 'extra_condition', render: (t: string) => t || '-' },
    {
        title: '模型预测',
        key: 'prediction',
        render: (_: any, record: any) => <Tag>{record.predicted_strategy}</Tag>
    },
    {
        title: '人工修正 (Final)',
        key: 'final',
        render: (_: any, record: any) => {
            const isEditable = record.status !== 'SYNCED';
            return (
                <Select 
                    defaultValue={record.final_strategy || record.predicted_strategy} 
                    style={{ width: 120 }} size="small" disabled={!isEditable}
                    onChange={(val) => handleReviewRule(record, 'REVIEWED', { final_strategy: val })}
                >
                    {strategyOptions.map(s => <Option key={s} value={s}>{s}</Option>)}
                </Select>
            );
        }
    },
    statusColumn,
    auditColumn,
    {
        title: '操作',
        key: 'action',
        render: (_: any, record: any) => (
            <Space>
                {record.status === 'PENDING' && (
                    <Tooltip title="确认通过">
                        <Button type="primary" size="small" icon={<CheckOutlined />} onClick={() => handleReviewRule(record, 'REVIEWED')} />
                    </Tooltip>
                )}
                {record.status !== 'IGNORED' && record.status !== 'SYNCED' && (
                    <Tooltip title="忽略">
                        <Button size="small" danger icon={<CloseOutlined />} onClick={() => handleReviewRule(record, 'IGNORED')} />
                    </Tooltip>
                )}
                {record.status === 'IGNORED' && (
                    <Popconfirm title="确定彻底删除?" onConfirm={() => handleDeleteRule(record.id)}>
                        <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
                    </Popconfirm>
                )}
            </Space>
        )
    }
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
    getCheckboxProps: (record: any) => ({
      disabled: record.status !== 'REVIEWED',
    }),
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>智能标注与审核 (Smart Labeling)</h2>
        <Space>
            {isAdmin && <Button onClick={handleImportMock}>导入 Mock 数据 ({activeTab})</Button>}
            {isAdmin && (
                <Button 
                    type="primary" 
                    icon={<CloudUploadOutlined />} 
                    disabled={selectedRowKeys.length === 0}
                    loading={syncing}
                    onClick={handleSync}
                >
                    批量入库 ({selectedRowKeys.length})
                </Button>
            )}
        </Space>
      </div>

      {renderHelpMessage()}

      <div style={{ marginBottom: 16 }}>
        <Radio.Group value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setSelectedRowKeys([]); }} buttonStyle="solid">
            <Radio.Button value="PENDING">待审核 (Pending)</Radio.Button>
            <Radio.Button value="REVIEWED">已审核 (Reviewed)</Radio.Button>
            <Radio.Button value="SYNCED">已入库 (Synced)</Radio.Button>
            <Radio.Button value="IGNORED">已忽略 (Ignored)</Radio.Button>
        </Radio.Group>
      </div>

      <Tabs activeKey={activeTab} onChange={(key) => { setActiveTab(key); setSelectedRowKeys([]); }} type="card">
        <TabPane tab="敏感词审核" key="keywords">
            <Table
                rowSelection={statusFilter === 'REVIEWED' && isAdmin ? rowSelection : undefined}
                columns={keywordColumns}
                dataSource={data}
                rowKey="id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />
        </TabPane>
        <TabPane tab="规则审核" key="rules">
            <Table
                rowSelection={statusFilter === 'REVIEWED' && isAdmin ? rowSelection : undefined}
                columns={rulesColumns}
                dataSource={rulesData}
                rowKey="id"
                loading={loading}
                pagination={{ pageSize: 10 }}
            />
        </TabPane>
      </Tabs>
    </div>
  );
};

export default SmartLabelingPage;

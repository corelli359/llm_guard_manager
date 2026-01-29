import React, { useState, useEffect } from 'react';
import { Table, Button, Tabs, Tag, Space, message, Select, Radio, Tooltip, Alert, Popconfirm, Card, Statistic, Progress } from 'antd';
import { CheckOutlined, CloseOutlined, CloudUploadOutlined, UserOutlined, DeleteOutlined, ClockCircleOutlined, FileTextOutlined } from '@ant-design/icons';
import { stagingApi, metaTagsApi } from '../api';
import { MetaTag } from '../types';
import dayjs from 'dayjs';

const { TabPane } = Tabs;
const { Option } = Select;

const SmartLabelingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('keywords');
  const [data, setData] = useState([]);
  const [rulesData, setRulesData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('CLAIMED');
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [metaTags, setMetaTags] = useState<MetaTag[]>([]);
  const [myTasksStats, setMyTasksStats] = useState<any>(null);
  const [countdown, setCountdown] = useState<string>('');
  const [claiming, setClaiming] = useState(false);
  const [showMyTasks, setShowMyTasks] = useState(true);

  // Static options
  const riskOptions = ['High', 'Medium', 'Low'];
  const strategyOptions = ['BLOCK', 'PASS', 'REWRITE'];

  const userRole = localStorage.getItem('user_role');
  const isAdmin = userRole === 'ADMIN';

  useEffect(() => {
    fetchMetaTags();
    fetchData();
    fetchMyTasksStats();
  }, [activeTab, statusFilter, showMyTasks]);

  // 倒计时定时器
  useEffect(() => {
    if (!myTasksStats?.expires_at) {
      setCountdown('');
      return;
    }

    const timer = setInterval(() => {
      const now = new Date().getTime();
      const expiresAt = new Date(myTasksStats.expires_at).getTime();
      const distance = expiresAt - now;

      if (distance < 0) {
        setCountdown('已超时');
        clearInterval(timer);
        fetchData();
        fetchMyTasksStats();
      } else {
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        setCountdown(`${minutes}:${seconds.toString().padStart(2, '0')}`);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [myTasksStats]);

  const fetchMetaTags = async () => {
    try {
      const res = await metaTagsApi.getAll();
      setMetaTags(res.data.filter(tag => tag.is_active));
    } catch (e) {
      message.error('获取标签列表失败');
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'keywords') {
          const res = await stagingApi.listKeywords(statusFilter, showMyTasks && statusFilter === 'CLAIMED');
          setData(res.data);
      } else {
          const res = await stagingApi.listRules(statusFilter, showMyTasks && statusFilter === 'CLAIMED');
          setRulesData(res.data);
      }
    } catch (e) {
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchMyTasksStats = async () => {
    try {
      const res = await stagingApi.getMyTasksStats(activeTab);
      setMyTasksStats(res.data);
    } catch (e) {
      console.error('获取任务统计失败', e);
    }
  };

  const handleClaimBatch = async () => {
    setClaiming(true);
    try {
      const res = await stagingApi.claimBatch(50, activeTab);
      message.success(`成功领取 ${res.data.claimed_count} 条任务`);
      setStatusFilter('CLAIMED');
      setShowMyTasks(true);
      fetchData();
      fetchMyTasksStats();
    } catch (e: any) {
      message.error(e.response?.data?.detail || '领取任务失败');
    } finally {
      setClaiming(false);
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
      fetchMyTasksStats();
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
      fetchMyTasksStats();
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

  const handleReleaseExpired = async () => {
      try {
          const res = await stagingApi.releaseExpired();
          message.success(`已释放 ${res.data.released_keywords + res.data.released_rules} 条超时任务`);
          fetchData();
          fetchMyTasksStats();
      } catch (e) {
          message.error('释放失败');
      }
  };

  // --- UI Helpers ---
  const renderTaskProgress = () => {
    if (!myTasksStats || myTasksStats.claimed_count === 0) {
      return (
        <Card size="small" style={{ marginBottom: 16 }}>
          <Space>
            <FileTextOutlined style={{ fontSize: 20 }} />
            <span>当前没有认领的任务</span>
            <Button type="primary" onClick={handleClaimBatch} loading={claiming}>
              领取新任务 (50条)
            </Button>
          </Space>
        </Card>
      );
    }

    const totalInBatch = myTasksStats.claimed_count + myTasksStats.reviewed_count + myTasksStats.ignored_count;
    const completed = myTasksStats.reviewed_count + myTasksStats.ignored_count;
    const progress = totalInBatch > 0 ? Math.round((completed / totalInBatch) * 100) : 0;

    return (
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space size="large">
            <Statistic
              title="当前批次进度"
              value={completed}
              suffix={`/ ${totalInBatch}`}
              prefix={<FileTextOutlined />}
            />
            <Statistic
              title="剩余时间"
              value={countdown}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: countdown === '已超时' ? '#cf1322' : '#3f8600' }}
            />
            <Statistic
              title="待标注"
              value={myTasksStats.claimed_count}
            />
            <Statistic
              title="已完成"
              value={myTasksStats.reviewed_count}
              valueStyle={{ color: '#3f8600' }}
            />
            <Statistic
              title="已忽略"
              value={myTasksStats.ignored_count}
              valueStyle={{ color: '#999' }}
            />
          </Space>
          <Progress percent={progress} status="active" />
          {countdown === '已超时' && (
            <Alert
              message="任务已超时，未完成的任务将被释放"
              type="warning"
              showIcon
              closable
            />
          )}
        </Space>
      </Card>
    );
  };

  const renderHelpMessage = () => (
      <Alert
        message="操作指引"
        description={
            <ul style={{ paddingLeft: 20, margin: 0 }}>
                <li><strong>领取任务</strong>: 点击"领取新任务"按钮，一次领取50条待标注数据，30分钟内完成</li>
                <li><strong>确认 (Confirm) <CheckOutlined /></strong>: 认可模型结果或已修正数据，标记为"已审核 (Reviewed)"。管理员可将其同步入库。</li>
                <li><strong>忽略 (Ignore) <CloseOutlined /></strong>: 认为数据无效，标记为"已忽略 (Ignored)"。忽略的数据不会入库，后续可删除。</li>
                <li><strong>入库 (Sync) <CloudUploadOutlined /></strong>: (仅管理员) 批量将"已审核"的数据写入正式环境。</li>
                <li><strong>超时释放</strong>: 30分钟后未完成的任务会自动释放，其他人可以继续标注</li>
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
                <Tag color={record.status === 'PENDING' ? 'blue' : record.status === 'CLAIMED' ? 'orange' : record.status === 'REVIEWED' ? 'green' : record.status === 'SYNCED' ? 'purple' : 'default'}>
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
        ) : record.claimed_by ? (
            <Tooltip title={`认领于 ${dayjs(record.claimed_at).format('YYYY-MM-DD HH:mm')}`}>
                <Tag icon={<UserOutlined />} color="orange">{record.claimed_by}</Tag>
            </Tooltip>
        ) : '-'
  };

  const keywordColumns = [
    { title: '敏感词', dataIndex: 'keyword', key: 'keyword' },
    {
        title: '模型预测',
        key: 'prediction',
        render: (_: any, record: any) => {
            const tagInfo = metaTags.find(t => t.tag_code === record.predicted_tag);
            return (
                <Space direction="vertical" size={0}>
                    <Tag>{record.predicted_tag}{tagInfo ? ` - ${tagInfo.tag_name}` : ''}</Tag>
                    <Tag color="orange" style={{fontSize: 10}}>{record.predicted_risk}</Tag>
                </Space>
            );
        }
    },
    {
        title: '人工修正 (Final)',
        key: 'final',
        render: (_: any, record: any) => {
            const isEditable = record.status !== 'SYNCED' && record.status !== 'REVIEWED' && record.status !== 'IGNORED';
            return (
                <Space direction="vertical" size={4}>
                    <Select
                        defaultValue={record.final_tag || record.predicted_tag}
                        style={{ width: 180 }} size="small" disabled={!isEditable}
                        onChange={(val) => handleReviewKeyword(record, 'REVIEWED', { final_tag: val })}
                        showSearch
                        optionFilterProp="children"
                    >
                        {metaTags.map(tag => (
                            <Option key={tag.tag_code} value={tag.tag_code}>
                                {tag.tag_code} - {tag.tag_name}
                            </Option>
                        ))}
                    </Select>
                    <Select
                        defaultValue={record.final_risk || record.predicted_risk}
                        style={{ width: 180 }} size="small" disabled={!isEditable}
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
                {record.status === 'CLAIMED' && (
                    <>
                        <Tooltip title="确认通过">
                            <Button type="primary" size="small" icon={<CheckOutlined />} onClick={() => handleReviewKeyword(record, 'REVIEWED')} />
                        </Tooltip>
                        <Tooltip title="忽略">
                            <Button size="small" danger icon={<CloseOutlined />} onClick={() => handleReviewKeyword(record, 'IGNORED')} />
                        </Tooltip>
                    </>
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
    {
        title: '标签',
        dataIndex: 'tag_code',
        key: 'tag_code',
        render: (tagCode: string) => {
            const tagInfo = metaTags.find(t => t.tag_code === tagCode);
            return <Tag color="blue">{tagCode}{tagInfo ? ` - ${tagInfo.tag_name}` : ''}</Tag>;
        }
    },
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
            const isEditable = record.status !== 'SYNCED' && record.status !== 'REVIEWED' && record.status !== 'IGNORED';
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
                {record.status === 'CLAIMED' && (
                    <>
                        <Tooltip title="确认通过">
                            <Button type="primary" size="small" icon={<CheckOutlined />} onClick={() => handleReviewRule(record, 'REVIEWED')} />
                        </Tooltip>
                        <Tooltip title="忽略">
                            <Button size="small" danger icon={<CloseOutlined />} onClick={() => handleReviewRule(record, 'IGNORED')} />
                        </Tooltip>
                    </>
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
            {isAdmin && <Button onClick={handleReleaseExpired}>释放超时任务</Button>}
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

      {renderTaskProgress()}
      {renderHelpMessage()}

      <div style={{ marginBottom: 16 }}>
        <Radio.Group value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setSelectedRowKeys([]); }} buttonStyle="solid">
            <Radio.Button value="CLAIMED">我的任务 (Claimed)</Radio.Button>
            <Radio.Button value="PENDING">待认领 (Pending)</Radio.Button>
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

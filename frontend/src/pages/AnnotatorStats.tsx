import React, { useState, useEffect } from 'react';
import { Card, Table, Statistic, Row, Col, Select, message, Spin } from 'antd';
import { UserOutlined, CheckCircleOutlined, CloseCircleOutlined, FileTextOutlined } from '@ant-design/icons';
import { stagingApi } from '../api';

const { Option } = Select;

interface AnnotatorStat {
  annotator: string;
  reviewed_count: number;
  ignored_count: number;
  total_count: number;
}

const AnnotatorStatsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [taskType, setTaskType] = useState('keywords');
  const [stats, setStats] = useState<AnnotatorStat[]>([]);

  useEffect(() => {
    fetchStats();
  }, [taskType]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await stagingApi.getAnnotatorStats(taskType);
      setStats(res.data);
    } catch (e) {
      message.error('获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 计算总计
  const totalReviewed = stats.reduce((sum, item) => sum + item.reviewed_count, 0);
  const totalIgnored = stats.reduce((sum, item) => sum + item.ignored_count, 0);
  const totalAll = stats.reduce((sum, item) => sum + item.total_count, 0);

  const columns = [
    {
      title: '标注员',
      dataIndex: 'annotator',
      key: 'annotator',
      render: (name: string) => (
        <span>
          <UserOutlined style={{ marginRight: 8 }} />
          {name}
        </span>
      ),
    },
    {
      title: '已审核',
      dataIndex: 'reviewed_count',
      key: 'reviewed_count',
      sorter: (a: AnnotatorStat, b: AnnotatorStat) => a.reviewed_count - b.reviewed_count,
      render: (count: number) => (
        <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
          <CheckCircleOutlined style={{ marginRight: 4 }} />
          {count}
        </span>
      ),
    },
    {
      title: '已忽略',
      dataIndex: 'ignored_count',
      key: 'ignored_count',
      sorter: (a: AnnotatorStat, b: AnnotatorStat) => a.ignored_count - b.ignored_count,
      render: (count: number) => (
        <span style={{ color: '#999' }}>
          <CloseCircleOutlined style={{ marginRight: 4 }} />
          {count}
        </span>
      ),
    },
    {
      title: '总计',
      dataIndex: 'total_count',
      key: 'total_count',
      sorter: (a: AnnotatorStat, b: AnnotatorStat) => a.total_count - b.total_count,
      render: (count: number) => (
        <span style={{ fontWeight: 'bold' }}>
          <FileTextOutlined style={{ marginRight: 4 }} />
          {count}
        </span>
      ),
    },
    {
      title: '完成率',
      key: 'completion_rate',
      sorter: (a: AnnotatorStat, b: AnnotatorStat) => {
        const rateA = a.total_count > 0 ? ((a.reviewed_count + a.ignored_count) / a.total_count) * 100 : 0;
        const rateB = b.total_count > 0 ? ((b.reviewed_count + b.ignored_count) / b.total_count) * 100 : 0;
        return rateA - rateB;
      },
      render: (_: any, record: AnnotatorStat) => {
        const rate = record.total_count > 0
          ? ((record.reviewed_count + record.ignored_count) / record.total_count) * 100
          : 0;
        return <span>{rate.toFixed(1)}%</span>;
      },
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2>标注员统计 (Annotator Statistics)</h2>
        <Select
          value={taskType}
          onChange={setTaskType}
          style={{ width: 200 }}
        >
          <Option value="keywords">敏感词审核</Option>
          <Option value="rules">规则审核</Option>
        </Select>
      </div>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总标注员数"
              value={stats.length}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总已审核"
              value={totalReviewed}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总已忽略"
              value={totalIgnored}
              valueStyle={{ color: '#999' }}
              prefix={<CloseCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总标注数"
              value={totalAll}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={stats}
            rowKey="annotator"
            pagination={{ pageSize: 10 }}
            locale={{ emptyText: '暂无标注数据' }}
          />
        </Spin>
      </Card>
    </div>
  );
};

export default AnnotatorStatsPage;

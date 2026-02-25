import React, { useEffect, useState } from 'react';
import { Card, Statistic, Row, Col, Table, Tag, Button, Space, Tooltip as AntTooltip } from 'antd';
import { ArrowLeftOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { EvalMetrics } from '../types';
import { evaluationApi, getErrorMessage } from '../api';
import { message } from 'antd';

const COLORS = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'];

const MetricLabel: React.FC<{ title: string; tip: string }> = ({ title, tip }) => (
  <span>{title} <AntTooltip title={tip}><QuestionCircleOutlined style={{ color: '#999', fontSize: 12 }} /></AntTooltip></span>
);

const EvalMetricsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<EvalMetrics | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!taskId) return;
    setLoading(true);
    evaluationApi.getMetrics(taskId)
      .then(res => setMetrics(res.data))
      .catch(err => message.error(getErrorMessage(err, '获取指标失败')))
      .finally(() => setLoading(false));
  }, [taskId]);

  if (loading || !metrics) return <div>加载中...</div>;

  const pct = (v: number) => `${((v || 0) * 100).toFixed(1)}%`;
  const byTag = metrics.by_tag || [];

  const tagColumns = [
    { title: '标签', dataIndex: 'tag_code', key: 'tag_code', render: (v: string) => <Tag color="blue">{v}</Tag> },
    { title: '总数', dataIndex: 'total', key: 'total' },
    { title: '拦截数', dataIndex: 'block_count', key: 'block_count' },
    { title: '准确率', dataIndex: 'accuracy', key: 'accuracy', render: pct },
    { title: '精确率', dataIndex: 'precision', key: 'precision', render: pct },
    { title: '召回率', dataIndex: 'recall', key: 'recall', render: pct },
    { title: 'F1', dataIndex: 'f1_score', key: 'f1_score', render: pct },
    { title: '漏检率', dataIndex: 'miss_rate', key: 'miss_rate', render: pct },
    { title: '误检率', dataIndex: 'false_positive_rate', key: 'false_positive_rate', render: pct },
  ];

  const barData = byTag.map(t => ({
    name: t.tag_code,
    准确率: +((t.accuracy || 0) * 100).toFixed(1),
    精确率: +((t.precision || 0) * 100).toFixed(1),
    召回率: +((t.recall || 0) * 100).toFixed(1),
    F1: +((t.f1_score || 0) * 100).toFixed(1),
  }));

  const pieData = byTag.map(t => ({ name: t.tag_code, value: t.total }));

  // 混淆矩阵数据
  const tp = metrics.tp || 0;
  const fn = metrics.fn || 0;
  const fp = metrics.fp || 0;
  const tn = metrics.tn || 0;

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/eval/tasks')}>返回任务列表</Button>
        <Button onClick={() => navigate(`/eval/tasks/${taskId}/results`)}>查看结果详情</Button>
      </Space>

      {/* 核心指标卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card><Statistic title={<MetricLabel title="准确率" tip="正确判定的样本数 / 总样本数，衡量整体判定能力" />} value={pct(metrics.accuracy)} valueStyle={{ color: (metrics.accuracy || 0) >= 0.85 ? '#52c41a' : '#f5222d' }} /></Card>
        </Col>
        <Col span={4}>
          <Card><Statistic title={<MetricLabel title="精确率" tip="正确拦截数 / 总拦截数，拦截的有多少是真违规" />} value={pct(metrics.precision)} valueStyle={{ color: (metrics.precision || 0) >= 0.85 ? '#52c41a' : '#faad14' }} /></Card>
        </Col>
        <Col span={4}>
          <Card><Statistic title={<MetricLabel title="召回率" tip="正确拦截数 / 总违规数，违规的有多少被拦住了" />} value={pct(metrics.recall)} valueStyle={{ color: (metrics.recall || 0) >= 0.85 ? '#52c41a' : '#faad14' }} /></Card>
        </Col>
        <Col span={4}>
          <Card><Statistic title={<MetricLabel title="F1 Score" tip="精确率和召回率的调和平均，综合衡量拦截效果" />} value={pct(metrics.f1_score)} valueStyle={{ color: (metrics.f1_score || 0) >= 0.85 ? '#52c41a' : '#faad14' }} /></Card>
        </Col>
        <Col span={4}>
          <Card><Statistic title={<MetricLabel title="漏检率" tip="违规样本中被放行的比例，越低越好" />} value={pct(metrics.miss_rate)} valueStyle={{ color: (metrics.miss_rate || 0) > 0.1 ? '#f5222d' : '#52c41a' }} /></Card>
        </Col>
        <Col span={4}>
          <Card><Statistic title={<MetricLabel title="误检率" tip="合规样本中被误拦截的比例，越低越好" />} value={pct(metrics.false_positive_rate)} valueStyle={{ color: (metrics.false_positive_rate || 0) > 0.1 ? '#faad14' : '#52c41a' }} /></Card>
        </Col>
      </Row>

      {/* 基础统计 + 混淆矩阵 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={3}><Card><Statistic title="总测评数" value={metrics.total} /></Card></Col>
        <Col span={3}><Card><Statistic title="拦截数" value={metrics.block_count || 0} /></Card></Col>
        <Col span={3}><Card><Statistic title="拦截率" value={pct(metrics.block_rate)} /></Card></Col>
        <Col span={3}><Card><Statistic title="平均耗时" value={`${metrics.avg_latency || 0}ms`} /></Card></Col>
        <Col span={12}>
          <Card title="混淆矩阵" size="small">
            <table style={{ width: '100%', textAlign: 'center', borderCollapse: 'collapse' }}>
              <thead>
                <tr><th style={{ border: '1px solid #f0f0f0', padding: 8, background: '#fafafa' }}></th><th style={{ border: '1px solid #f0f0f0', padding: 8, background: '#fafafa' }}>预测: 拦截</th><th style={{ border: '1px solid #f0f0f0', padding: 8, background: '#fafafa' }}>预测: 放行</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ border: '1px solid #f0f0f0', padding: 8, background: '#fafafa', fontWeight: 600 }}>实际: 违规</td>
                  <td style={{ border: '1px solid #f0f0f0', padding: 8, background: '#f6ffed', color: '#52c41a', fontWeight: 600 }}>TP={tp}</td>
                  <td style={{ border: '1px solid #f0f0f0', padding: 8, background: '#fff2f0', color: '#f5222d', fontWeight: 600 }}>FN={fn} (漏检)</td>
                </tr>
                <tr>
                  <td style={{ border: '1px solid #f0f0f0', padding: 8, background: '#fafafa', fontWeight: 600 }}>实际: 合规</td>
                  <td style={{ border: '1px solid #f0f0f0', padding: 8, background: '#fffbe6', color: '#faad14', fontWeight: 600 }}>FP={fp} (误检)</td>
                  <td style={{ border: '1px solid #f0f0f0', padding: 8, background: '#f6ffed', color: '#52c41a', fontWeight: 600 }}>TN={tn}</td>
                </tr>
              </tbody>
            </table>
          </Card>
        </Col>
      </Row>

      {/* 图表 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="按标签维度指标对比 (%)">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="准确率" fill="#1890ff" />
                <Bar dataKey="精确率" fill="#52c41a" />
                <Bar dataKey="召回率" fill="#faad14" />
                <Bar dataKey="F1" fill="#722ed1" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="风险类型分布">
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Card title="各标签详细指标">
        <Table columns={tagColumns} dataSource={byTag} rowKey="tag_code" pagination={false} />
      </Card>
    </div>
  );
};

export default EvalMetricsPage;

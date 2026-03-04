import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Statistic, Select, DatePicker, Space, Button, Table, message, Spin, Empty, Tag, Modal, Input, Tooltip, Switch } from 'antd';
import {
  CheckCircleOutlined, EditOutlined, StopOutlined, FieldTimeOutlined,
  ReloadOutlined, CloudUploadOutlined, QuestionCircleOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { Dayjs } from 'dayjs';
import { metricsApi } from '../api';

const { RangePicker } = DatePicker;

const MetricsDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [etlLoading, setEtlLoading] = useState(false);
  const [apps, setApps] = useState<string[]>([]);
  const [selectedApp, setSelectedApp] = useState<string | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);
  const [overview, setOverview] = useState<any>(null);
  const [riskData, setRiskData] = useState<any>(null);
  const [ruleData, setRuleData] = useState<any>(null);
  const [etlModalOpen, setEtlModalOpen] = useState(false);
  const [logDir, setLogDir] = useState('');
  const [etlFull, setEtlFull] = useState(false);

  const getParams = useCallback(() => {
    const params: any = {};
    if (selectedApp) params.app_id = selectedApp;
    if (dateRange?.[0]) params.date_start = dateRange[0].format('YYYY-MM-DD');
    if (dateRange?.[1]) params.date_end = dateRange[1].format('YYYY-MM-DD');
    return params;
  }, [selectedApp, dateRange]);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const params = getParams();
      const [ovRes, riskRes, ruleRes] = await Promise.all([
        metricsApi.getOverview(params),
        metricsApi.getRiskDistribution(params),
        metricsApi.getRuleQuality(params),
      ]);
      setOverview(ovRes.data);
      setRiskData(riskRes.data);
      setRuleData(ruleRes.data);
    } catch (e: any) {
      message.error('加载指标失败: ' + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  }, [getParams]);

  const fetchApps = async () => {
    try {
      const res = await metricsApi.getApps();
      setApps(res.data.apps || []);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchApps(); }, []);
  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleEtl = async () => {
    setEtlLoading(true);
    try {
      const res = await metricsApi.runEtl(logDir || undefined, undefined, etlFull);
      message.success(`${res.data.mode}加工完成: 处理 ${res.data.stats.processed} 条，跳过重复 ${res.data.stats.skipped_dup} 条，无变化文件 ${res.data.stats.skipped_unchanged} 个`);
      setEtlModalOpen(false);
      fetchApps();
      fetchAll();
    } catch (e: any) {
      message.error('加工失败: ' + (e.response?.data?.detail || e.message));
    } finally {
      setEtlLoading(false);
    }
  };

  const s = overview?.summary || {};
  const lat = overview?.latency || {};
  const trend = overview?.trend || [];

  /** 指标说明 Tooltip */
  const Tip: React.FC<{ text: string }> = ({ text }) => (
    <Tooltip title={text}>
      <QuestionCircleOutlined style={{ color: '#999', marginLeft: 4, cursor: 'help' }} />
    </Tooltip>
  );

  // 趋势折线图
  const trendOption = {
    tooltip: { trigger: 'axis' as const },
    legend: { data: ['通过率', '改写率', '阻断率'] },
    xAxis: { type: 'category' as const, data: trend.map((t: any) => t.date) },
    yAxis: { type: 'value' as const, axisLabel: { formatter: '{value}%' } },
    series: [
      { name: '通过率', type: 'line', data: trend.map((t: any) => t.passRate), smooth: true, itemStyle: { color: '#52c41a' } },
      { name: '改写率', type: 'line', data: trend.map((t: any) => t.rewriteRate), smooth: true, itemStyle: { color: '#faad14' } },
      { name: '阻断率', type: 'line', data: trend.map((t: any) => t.blockRate), smooth: true, itemStyle: { color: '#ff4d4f' } },
    ],
  };

  // 决策分布饼图
  const pieOption = {
    tooltip: { trigger: 'item' as const },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      data: [
        { value: s.pass_count || 0, name: '通过', itemStyle: { color: '#52c41a' } },
        { value: s.rewrite_count || 0, name: '改写', itemStyle: { color: '#faad14' } },
        { value: s.block_count || 0, name: '阻断', itemStyle: { color: '#ff4d4f' } },
        { value: s.review_count || 0, name: '审核', itemStyle: { color: '#1890ff' } },
      ].filter(d => d.value > 0),
      label: { formatter: '{b}: {d}%' },
    }],
  };

  // 风险标签柱状图
  const tagDist = riskData?.tag_distribution || [];
  const tagBarOption = {
    tooltip: { trigger: 'axis' as const },
    xAxis: { type: 'category' as const, data: tagDist.slice(0, 10).map((t: any) => t.tag), axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value' as const },
    series: [{ type: 'bar', data: tagDist.slice(0, 10).map((t: any) => t.count), itemStyle: { color: '#1890ff' } }],
  };

  // 时延趋势图
  const latencyOption = {
    tooltip: { trigger: 'axis' as const },
    legend: { data: ['平均', 'P95', 'P99'] },
    xAxis: { type: 'category' as const, data: trend.map((t: any) => t.date) },
    yAxis: { type: 'value' as const, axisLabel: { formatter: '{value}ms' } },
    series: [
      { name: '平均', type: 'line', data: trend.map((t: any) => t.avgMs), smooth: true },
      { name: 'P95', type: 'line', data: trend.map((t: any) => t.p95Ms), smooth: true, lineStyle: { type: 'dashed' as const } },
      { name: 'P99', type: 'line', data: trend.map((t: any) => t.p99Ms), smooth: true, lineStyle: { type: 'dashed' as const } },
    ],
  };

  // 规则贡献度
  const ruleHits = ruleData?.rule_hit_distribution || [];
  const ruleColumns = [
    { title: '规则标签', dataIndex: 'tag', key: 'tag', render: (v: string) => <Tag>{v}</Tag> },
    { title: '命中次数', dataIndex: 'count', key: 'count', sorter: (a: any, b: any) => a.count - b.count },
    { title: '贡献度', dataIndex: 'contribution_pct', key: 'pct', render: (v: number) => `${v}%` },
  ];

  const wordHits = riskData?.top_hit_words || [];
  const wordColumns = [
    { title: '敏感词', dataIndex: 'word', key: 'word' },
    { title: '命中次数', dataIndex: 'count', key: 'count', sorter: (a: any, b: any) => a.count - b.count },
  ];

  const noData = !overview || overview.total_requests === 0;

  return (
    <div>
      {/* 筛选栏 */}
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          allowClear placeholder="全部场景" style={{ width: 180 }}
          value={selectedApp} onChange={setSelectedApp}
          options={apps.map(a => ({ label: a, value: a }))}
        />
        <RangePicker value={dateRange as any} onChange={(v) => setDateRange(v as any)} />
        <Button icon={<ReloadOutlined />} onClick={fetchAll} loading={loading}>刷新</Button>
        <Button icon={<CloudUploadOutlined />} onClick={() => setEtlModalOpen(true)}>日志加工</Button>
      </Space>

      {loading ? <Spin size="large" style={{ display: 'block', margin: '80px auto' }} /> : noData ? (
        <Empty description="暂无数据，请先进行日志加工" />
      ) : (
        <>
          {/* 概览卡片 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Card><Statistic title={<>总请求数<Tip text="统计周期内所有经过围栏服务的请求总量，包含通过、改写、阻断、审核和错误请求" /></>} value={s.total_requests || 0} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title={<>安全通过率<Tip text="判定为安全（score=0）的请求占总请求的百分比。计算公式：通过数 / 总请求数 × 100%" /></>} value={s.pass_rate || 0} suffix="%" prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title={<>意图改写率<Tip text="触发意图改写（score=50）的请求占总请求的百分比。改写指内容被自动修正后放行" /></>} value={s.rewrite_rate || 0} suffix="%" prefix={<EditOutlined style={{ color: '#faad14' }} />} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title={<>直接阻断率<Tip text="被直接拦截（score=100）的请求占总请求的百分比。阻断指内容命中高风险规则被禁止通过" /></>} value={s.block_rate || 0} suffix="%" prefix={<StopOutlined style={{ color: '#ff4d4f' }} />} /></Card>
            </Col>
          </Row>

          {/* 趋势 + 饼图 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={16}>
              <Card title={<>请求处理趋势<Tip text="按天聚合的通过率、改写率、阻断率变化趋势。用于观察安全态势的时间演变" /></>} size="small">
                <ReactECharts option={trendOption} style={{ height: 280 }} />
              </Card>
            </Col>
            <Col span={8}>
              <Card title={<>决策分布<Tip text="各决策类型的请求数量占比。score=0 通过，score=50 改写，score=100 阻断，score=1000 人工审核" /></>} size="small">
                <ReactECharts option={pieOption} style={{ height: 280 }} />
              </Card>
            </Col>
          </Row>

          {/* 风险分布 + 敏感词 TOP */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={14}>
              <Card title={<>风险标签分布 TOP10<Tip text="按标签编码（如 A.2.20）聚合的命中次数排名。标签从规则名中提取，同一标签下不同安全等级的命中合并统计" /></>} size="small">
                {tagDist.length > 0 ? <ReactECharts option={tagBarOption} style={{ height: 280 }} /> : <Empty />}
              </Card>
            </Col>
            <Col span={10}>
              <Card title={<>敏感词命中 TOP<Tip text="命中频率最高的敏感词排名。统计所有触发拦截或改写的敏感词出现次数，用于评估词库有效性" /></>} size="small">
                <Table dataSource={wordHits} columns={wordColumns} rowKey="word" size="small" pagination={false} scroll={{ y: 240 }} />
              </Card>
            </Col>
          </Row>

          {/* 时延 + 规则质量 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Card title={<>处理时延趋势<Tip text="围栏服务处理每个请求的耗时统计。平均值反映整体性能，P95/P99 反映长尾延迟。时延包含规则匹配、敏感词检测等全链路耗时" /></>} size="small" extra={
                <Space>
                  <Tag icon={<FieldTimeOutlined />}>平均 {lat.avg_ms ?? '-'}ms</Tag>
                  <Tag color="orange">P95 {lat.p95_ms ?? '-'}ms</Tag>
                  <Tag color="red">P99 {lat.p99_ms ?? '-'}ms</Tag>
                </Space>
              }>
                <ReactECharts option={latencyOption} style={{ height: 280 }} />
              </Card>
            </Col>
            <Col span={12}>
              <Card title={<>规则命中贡献度<Tip text="每条规则（如 A.1.9-CONTROVERSIAL）的命中次数及其占总命中的百分比。用于识别核心拦截规则和长期零命中的过时规则" /></>} size="small">
                <Table dataSource={ruleHits.slice(0, 10)} columns={ruleColumns} rowKey="tag" size="small" pagination={false} scroll={{ y: 240 }} />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* ETL 弹窗 */}
      <Modal title="日志加工" open={etlModalOpen} onCancel={() => setEtlModalOpen(false)}
        onOk={handleEtl} confirmLoading={etlLoading} okText="开始加工">
        <p>将原始日志（audit.log / request.log）展平为 JSONL 格式，按场景和日期分文件存储。</p>
        <p style={{ color: '#666', fontSize: 12 }}>增量模式只处理上次加工后新增的日志行，避免重复。全量模式会忽略历史记录从头处理。</p>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input placeholder="日志目录路径（留空使用默认配置）" value={logDir} onChange={e => setLogDir(e.target.value)} />
          <Space>
            <Switch checked={etlFull} onChange={setEtlFull} />
            <span>全量模式（清除增量记录，从头处理）</span>
          </Space>
        </Space>
      </Modal>
    </div>
  );
};

export default MetricsDashboard;

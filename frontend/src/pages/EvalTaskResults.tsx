import React, { useEffect, useState } from 'react';
import { Table, Tag, Space, Select, Button, Descriptions } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { EvalTaskResult, EvalTask } from '../types';
import { evaluationApi, getErrorMessage } from '../api';
import { message } from 'antd';

const EvalTaskResultsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [results, setResults] = useState<EvalTaskResult[]>([]);
  const [task, setTask] = useState<EvalTask | null>(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [filterResult, setFilterResult] = useState<string | undefined>();
  const [filterCorrect, setFilterCorrect] = useState<boolean | undefined>();

  const fetchResults = async () => {
    if (!taskId) return;
    setLoading(true);
    try {
      const res = await evaluationApi.getTaskResults(taskId, {
        skip: (page - 1) * pageSize, limit: pageSize,
        guardrail_result: filterResult, is_correct: filterCorrect,
      });
      setResults(res.data.items);
      setTotal(res.data.total);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取结果失败'));
    } finally {
      setLoading(false);
    }
  };

  const fetchTask = async () => {
    if (!taskId) return;
    try {
      const res = await evaluationApi.getTask(taskId);
      setTask(res.data);
    } catch {}
  };

  useEffect(() => { fetchTask(); }, [taskId]);
  useEffect(() => { fetchResults(); }, [taskId, page, pageSize, filterResult, filterCorrect]);

  const columns = [
    { title: '话术内容', dataIndex: 'content', key: 'content', ellipsis: true, width: 250 },
    {
      title: '标签', dataIndex: 'tag_codes', key: 'tag_codes',
      render: (v: string[]) => v?.map(t => <Tag key={t} color="blue">{t}</Tag>) || '-',
    },
    {
      title: '预期', dataIndex: 'expected_result', key: 'expected_result',
      render: (v: string) => <Tag color={v === 'VIOLATION' ? 'red' : 'green'}>{v === 'VIOLATION' ? '违规' : '合规'}</Tag>,
    },
    {
      title: '围栏结果', dataIndex: 'guardrail_result', key: 'guardrail_result',
      render: (v: string) => v ? <Tag color={v === 'BLOCK' ? 'red' : v === 'PASS' ? 'green' : 'default'}>{v}</Tag> : '-',
    },
    { title: '围栏分数', dataIndex: 'guardrail_score', key: 'guardrail_score', render: (v: number) => v ?? '-' },
    { title: '耗时(ms)', dataIndex: 'guardrail_latency', key: 'guardrail_latency', render: (v: number) => v ?? '-' },
    {
      title: 'LLM判定', dataIndex: 'llm_judgment', key: 'llm_judgment',
      render: (v: string) => v ? <Tag color={v === 'VIOLATION' ? 'red' : 'green'}>{v === 'VIOLATION' ? '违规' : '合规'}</Tag> : '-',
    },
    { title: 'LLM理由', dataIndex: 'llm_reason', key: 'llm_reason', ellipsis: true, width: 200 },
    {
      title: '一致性', dataIndex: 'is_consistent', key: 'is_consistent',
      render: (v: boolean | null) => v === null ? '-' : v ? <Tag color="green">一致</Tag> : <Tag color="orange">不一致</Tag>,
    },
    {
      title: '正确性', dataIndex: 'is_correct', key: 'is_correct',
      render: (v: boolean | null) => v === null ? '-' : v ? <Tag color="green">正确</Tag> : <Tag color="red">错误</Tag>,
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/eval/tasks')}>返回任务列表</Button>
        <Button onClick={() => navigate(`/eval/tasks/${taskId}/metrics`)}>查看指标统计</Button>
      </Space>

      {task && (
        <Descriptions bordered size="small" style={{ marginBottom: 16 }} column={4}>
          <Descriptions.Item label="任务名称">{task.task_name}</Descriptions.Item>
          <Descriptions.Item label="场景">{task.app_id}</Descriptions.Item>
          <Descriptions.Item label="状态"><Tag color={task.status === 'COMPLETED' ? 'success' : 'default'}>{task.status}</Tag></Descriptions.Item>
          <Descriptions.Item label="进度">{task.completed_cases + task.failed_cases} / {task.total_cases}</Descriptions.Item>
        </Descriptions>
      )}

      <Space style={{ marginBottom: 16 }}>
        <Select placeholder="围栏结果" allowClear style={{ width: 120 }} onChange={v => { setFilterResult(v); setPage(1); }}>
          <Select.Option value="BLOCK">BLOCK</Select.Option>
          <Select.Option value="PASS">PASS</Select.Option>
          <Select.Option value="ERROR">ERROR</Select.Option>
        </Select>
        <Select placeholder="正确性" allowClear style={{ width: 120 }} onChange={v => { setFilterCorrect(v); setPage(1); }}>
          <Select.Option value={true}>正确</Select.Option>
          <Select.Option value={false}>错误</Select.Option>
        </Select>
      </Space>

      <Table columns={columns} dataSource={results} rowKey="id" loading={loading} scroll={{ x: 1400 }}
        pagination={{ current: page, pageSize, total, onChange: (p, s) => { setPage(p); setPageSize(s || 50); } }} />
    </div>
  );
};

export default EvalTaskResultsPage;
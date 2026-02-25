import React, { useEffect, useState, useRef } from 'react';
import { Table, Button, Card, Form, Input, Select, InputNumber, Space, message, Tag, Progress, Popconfirm } from 'antd';
import { PlayCircleOutlined, StopOutlined, DeleteOutlined, BarChartOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { EvalTask, ScenarioApp, MetaTag } from '../types';
import { evaluationApi, scenariosApi, metaTagsApi, getErrorMessage } from '../api';

const statusColors: Record<string, string> = {
  PENDING: 'default', RUNNING: 'processing', COMPLETED: 'success', FAILED: 'error', CANCELLED: 'warning',
};
const statusLabels: Record<string, string> = {
  PENDING: '等待中', RUNNING: '运行中', COMPLETED: '已完成', FAILED: '失败', CANCELLED: '已取消',
};

const EvalTasksPage: React.FC = () => {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<EvalTask[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [apps, setApps] = useState<ScenarioApp[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [matchCount, setMatchCount] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [page, setPage] = useState(1);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [form] = Form.useForm();

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const res = await evaluationApi.listTasks({ skip: (page - 1) * 20, limit: 20 });
      setTasks(res.data.items);
      setTotal(res.data.total);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取任务列表失败'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    scenariosApi.getAll().then(r => setApps(r.data)).catch(() => {});
    metaTagsApi.getAll().then(r => setTags(r.data)).catch(() => {});
  }, []);

  useEffect(() => { fetchTasks(); }, [page]);

  // 轮询运行中的任务
  useEffect(() => {
    const hasRunning = tasks.some(t => t.status === 'RUNNING' || t.status === 'PENDING');
    if (hasRunning) {
      pollingRef.current = setInterval(fetchTasks, 2000);
    }
    return () => { if (pollingRef.current) clearInterval(pollingRef.current); };
  }, [tasks]);

  const handlePreviewCount = async () => {
    const values = form.getFieldsValue();
    try {
      const tagStr = values.filter_tag_codes?.join(',') || undefined;
      const res = await evaluationApi.countTestCases({ tag_codes: tagStr, expected_result: values.filter_expected_result });
      setMatchCount(res.data.count);
    } catch { setMatchCount(null); }
  };

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      setCreating(true);
      await evaluationApi.createTask(values);
      message.success('任务已创建并开始执行');
      form.resetFields();
      setMatchCount(null);
      fetchTasks();
    } catch (error: any) {
      if (!error.errorFields) message.error(getErrorMessage(error, '创建失败'));
    } finally {
      setCreating(false);
    }
  };

  const handleCancel = async (id: string) => {
    try {
      await evaluationApi.cancelTask(id);
      message.success('已取消');
      fetchTasks();
    } catch (error: any) {
      message.error(getErrorMessage(error, '取消失败'));
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await evaluationApi.deleteTask(id);
      message.success('已删除');
      fetchTasks();
    } catch (error: any) {
      message.error(getErrorMessage(error, '删除失败'));
    }
  };

  const columns = [
    { title: '任务名称', dataIndex: 'task_name', key: 'task_name' },
    { title: '场景', dataIndex: 'app_id', key: 'app_id' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={statusColors[s]}>{statusLabels[s] || s}</Tag>,
    },
    {
      title: '进度', key: 'progress',
      render: (_: any, r: EvalTask) => (
        <Progress percent={r.total_cases ? Math.round((r.completed_cases + r.failed_cases) / r.total_cases * 100) : 0}
          size="small" status={r.status === 'FAILED' ? 'exception' : undefined}
          format={() => `${r.completed_cases + r.failed_cases}/${r.total_cases}`} />
      ),
    },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', render: (v: string) => v ? new Date(v).toLocaleString() : '-' },
    {
      title: '操作', key: 'action',
      render: (_: any, r: EvalTask) => (
        <Space>
          {r.status === 'RUNNING' && <Button size="small" icon={<StopOutlined />} onClick={() => handleCancel(r.id)}>取消</Button>}
          {(r.status === 'COMPLETED' || r.status === 'CANCELLED') && (
            <>
              <Button size="small" icon={<UnorderedListOutlined />} onClick={() => navigate(`/eval/tasks/${r.id}/results`)}>结果</Button>
              <Button size="small" icon={<BarChartOutlined />} onClick={() => navigate(`/eval/tasks/${r.id}/metrics`)}>指标</Button>
            </>
          )}
          {r.status !== 'RUNNING' && (
            <Popconfirm title="确定删除？" onConfirm={() => handleDelete(r.id)} okText="确定" cancelText="取消">
              <Button size="small" icon={<DeleteOutlined />} danger />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <h2>测评任务</h2>
      <Card title="创建测评任务" style={{ marginBottom: 16 }}>
        <Form form={form} layout="inline" onValuesChange={handlePreviewCount}>
          <Form.Item name="task_name" label="任务名称" rules={[{ required: true, message: '请输入' }]}>
            <Input placeholder="例如：V1.2全量测评" style={{ width: 180 }} />
          </Form.Item>
          <Form.Item name="app_id" label="场景" rules={[{ required: true, message: '请选择' }]}>
            <Select placeholder="选择场景" style={{ width: 160 }}>
              {apps.map(a => <Select.Option key={a.app_id} value={a.app_id}>{a.app_name}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="concurrency" label="并发数" initialValue={5}>
            <InputNumber min={1} max={20} />
          </Form.Item>
          <Form.Item name="filter_tag_codes" label="标签筛选">
            <Select mode="multiple" placeholder="全部" allowClear style={{ width: 200 }}>
              {tags.filter(t => t.level === 2).map(t => <Select.Option key={t.tag_code} value={t.tag_code}>{t.tag_name}</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="filter_expected_result" label="预期结果">
            <Select placeholder="全部" allowClear style={{ width: 100 }}>
              <Select.Option value="VIOLATION">违规</Select.Option>
              <Select.Option value="COMPLIANT">合规</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              {matchCount !== null && <Tag>匹配 {matchCount} 题</Tag>}
              <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleCreate} loading={creating}>创建并执行</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Table columns={columns} dataSource={tasks} rowKey="id" loading={loading}
        pagination={{ current: page, pageSize: 20, total, onChange: p => setPage(p) }} />
    </div>
  );
};

export default EvalTasksPage;

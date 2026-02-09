import React, { useState, useEffect } from 'react';
import { Table, Card, Form, Input, Select, DatePicker, Button, Space, Tag, Drawer, message } from 'antd';
import { SearchOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import { auditLogsApi, getErrorMessage } from '../api';
import { AuditLog } from '../types';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [detailDrawerOpen, setDetailDrawerOpen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchLogs();
  }, [currentPage, pageSize]);

  const fetchLogs = async (filters?: any) => {
    setLoading(true);
    try {
      const params = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        ...filters,
      };
      const res = await auditLogsApi.queryLogs(params);
      setLogs(res.data.items || res.data);
      setTotal(res.data.total || res.data.length);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取审计日志失败'));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (values: any) => {
    const filters: any = {};

    if (values.username) filters.username = values.username;
    if (values.action) filters.action = values.action;
    if (values.resource_type) filters.resource_type = values.resource_type;
    if (values.scenario_id) filters.scenario_id = values.scenario_id;

    if (values.date_range) {
      filters.start_date = values.date_range[0].format('YYYY-MM-DD HH:mm:ss');
      filters.end_date = values.date_range[1].format('YYYY-MM-DD HH:mm:ss');
    }

    setCurrentPage(1);
    fetchLogs(filters);
  };

  const handleReset = () => {
    form.resetFields();
    setCurrentPage(1);
    fetchLogs();
  };

  const showDetail = (log: AuditLog) => {
    setSelectedLog(log);
    setDetailDrawerOpen(true);
  };

  const getActionColor = (action: string) => {
    const colorMap: Record<string, string> = {
      CREATE: 'green',
      UPDATE: 'blue',
      DELETE: 'red',
      VIEW: 'default',
      EXPORT: 'orange',
    };
    return colorMap[action] || 'default';
  };

  const columns = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      width: 120,
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 100,
      render: (action: string) => (
        <Tag color={getActionColor(action)}>{action}</Tag>
      ),
    },
    {
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
      width: 150,
    },
    {
      title: '资源ID',
      dataIndex: 'resource_id',
      key: 'resource_id',
      width: 200,
      ellipsis: true,
    },
    {
      title: '场景ID',
      dataIndex: 'scenario_id',
      key: 'scenario_id',
      width: 150,
      ellipsis: true,
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
    },
    {
      title: '操作',
      key: 'action_btn',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: AuditLog) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => showDetail(record)}
        >
          详情
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card title="审计日志查询" style={{ marginBottom: 16 }}>
        <Form form={form} onFinish={handleSearch} layout="inline">
          <Form.Item name="username" label="用户名">
            <Input placeholder="输入用户名" style={{ width: 150 }} />
          </Form.Item>
          <Form.Item name="action" label="操作类型">
            <Select placeholder="选择操作" style={{ width: 150 }} allowClear>
              <Select.Option value="CREATE">CREATE</Select.Option>
              <Select.Option value="UPDATE">UPDATE</Select.Option>
              <Select.Option value="DELETE">DELETE</Select.Option>
              <Select.Option value="VIEW">VIEW</Select.Option>
              <Select.Option value="EXPORT">EXPORT</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="resource_type" label="资源类型">
            <Select placeholder="选择资源类型" style={{ width: 150 }} allowClear>
              <Select.Option value="USER">USER</Select.Option>
              <Select.Option value="SCENARIO">SCENARIO</Select.Option>
              <Select.Option value="KEYWORD">KEYWORD</Select.Option>
              <Select.Option value="POLICY">POLICY</Select.Option>
              <Select.Option value="META_TAG">META_TAG</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="scenario_id" label="场景ID">
            <Input placeholder="输入场景ID" style={{ width: 150 }} />
          </Form.Item>
          <Form.Item name="date_range" label="时间范围">
            <RangePicker showTime />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                查询
              </Button>
              <Button onClick={handleReset} icon={<ReloadOutlined />}>
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title={`审计日志列表 (共 ${total} 条)`}>
        <Table
          dataSource={logs}
          columns={columns}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1400 }}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
            },
          }}
        />
      </Card>

      <Drawer
        title="审计日志详情"
        placement="right"
        width={600}
        open={detailDrawerOpen}
        onClose={() => setDetailDrawerOpen(false)}
      >
        {selectedLog && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <strong>日志ID:</strong> {selectedLog.id}
            </div>
            <div style={{ marginBottom: 16 }}>
              <strong>用户:</strong> {selectedLog.username} (ID: {selectedLog.user_id})
            </div>
            <div style={{ marginBottom: 16 }}>
              <strong>操作:</strong> <Tag color={getActionColor(selectedLog.action)}>{selectedLog.action}</Tag>
            </div>
            <div style={{ marginBottom: 16 }}>
              <strong>资源类型:</strong> {selectedLog.resource_type}
            </div>
            {selectedLog.resource_id && (
              <div style={{ marginBottom: 16 }}>
                <strong>资源ID:</strong> {selectedLog.resource_id}
              </div>
            )}
            {selectedLog.scenario_id && (
              <div style={{ marginBottom: 16 }}>
                <strong>场景ID:</strong> {selectedLog.scenario_id}
              </div>
            )}
            <div style={{ marginBottom: 16 }}>
              <strong>IP地址:</strong> {selectedLog.ip_address || 'N/A'}
            </div>
            <div style={{ marginBottom: 16 }}>
              <strong>User Agent:</strong>
              <div style={{ wordBreak: 'break-all', fontSize: 12, color: '#666' }}>
                {selectedLog.user_agent || 'N/A'}
              </div>
            </div>
            <div style={{ marginBottom: 16 }}>
              <strong>时间:</strong> {dayjs(selectedLog.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </div>
            {selectedLog.details && (
              <div>
                <strong>详细信息:</strong>
                <pre style={{
                  background: '#f5f5f5',
                  padding: 12,
                  borderRadius: 4,
                  marginTop: 8,
                  overflow: 'auto',
                  maxHeight: 400,
                }}>
                  {JSON.stringify(selectedLog.details, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default AuditLogsPage;

import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Tag, Upload } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined } from '@ant-design/icons';
import { EvalTestCase, MetaTag } from '../types';
import { evaluationApi, metaTagsApi, getErrorMessage } from '../api';

const { Search, TextArea } = Input;

const EvalTestCasesPage: React.FC = () => {
  const [cases, setCases] = useState<EvalTestCase[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [searchText, setSearchText] = useState('');
  const [filterTag, setFilterTag] = useState<string | undefined>();
  const [filterExpected, setFilterExpected] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [form] = Form.useForm();

  const fetchCases = async () => {
    setLoading(true);
    try {
      const res = await evaluationApi.listTestCases({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        keyword: searchText || undefined,
        tag_code: filterTag,
        expected_result: filterExpected,
      });
      setCases(res.data.items);
      setTotal(res.data.total);
    } catch (error: any) {
      message.error(getErrorMessage(error, '获取题库失败'));
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const res = await metaTagsApi.getAll();
      setTags(res.data);
    } catch {}
  };

  useEffect(() => { fetchTags(); }, []);
  useEffect(() => { fetchCases(); }, [page, pageSize, searchText, filterTag, filterExpected]);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({ is_active: true, expected_result: 'VIOLATION' });
    setIsModalOpen(true);
  };

  const handleEdit = (record: EvalTestCase) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await evaluationApi.deleteTestCase(id);
      message.success('已删除');
      fetchCases();
    } catch (error: any) {
      message.error(getErrorMessage(error, '删除失败'));
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await evaluationApi.updateTestCase(editingId, values);
        message.success('已更新');
      } else {
        await evaluationApi.createTestCase(values);
        message.success('已创建');
      }
      setIsModalOpen(false);
      fetchCases();
    } catch (error: any) {
      if (!error.errorFields) message.error(getErrorMessage(error, '操作失败'));
    }
  };

  const handleImport = async (file: File) => {
    try {
      const res = await evaluationApi.importTestCases(file);
      message.success(res.data.detail);
      fetchCases();
    } catch (error: any) {
      message.error(getErrorMessage(error, '导入失败'));
    }
    return false; // prevent default upload
  };

  const columns = [
    { title: '话术内容', dataIndex: 'content', key: 'content', ellipsis: true, width: 300 },
    {
      title: '标签', dataIndex: 'tag_codes', key: 'tag_codes',
      render: (tags: string[]) => tags?.map(t => <Tag key={t} color="blue">{t}</Tag>) || '-',
    },
    { title: '风险点', dataIndex: 'risk_point', key: 'risk_point', ellipsis: true, width: 150 },
    {
      title: '预期结果', dataIndex: 'expected_result', key: 'expected_result',
      render: (v: string) => <Tag color={v === 'VIOLATION' ? 'red' : 'green'}>{v === 'VIOLATION' ? '违规' : '合规'}</Tag>,
    },
    {
      title: '状态', dataIndex: 'is_active', key: 'is_active',
      render: (v: boolean) => <Switch size="small" checked={v} disabled />,
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: EvalTestCase) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button size="small" icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>测评题库</h2>
        <Space>
          <Search placeholder="搜索话术..." onSearch={v => { setSearchText(v); setPage(1); }} enterButton allowClear style={{ width: 250 }} />
          <Select placeholder="标签筛选" allowClear style={{ width: 140 }} onChange={v => { setFilterTag(v); setPage(1); }}>
            {tags.filter(t => t.level === 2).map(t => <Select.Option key={t.tag_code} value={t.tag_code}>{t.tag_name}</Select.Option>)}
          </Select>
          <Select placeholder="预期结果" allowClear style={{ width: 120 }} onChange={v => { setFilterExpected(v); setPage(1); }}>
            <Select.Option value="VIOLATION">违规</Select.Option>
            <Select.Option value="COMPLIANT">合规</Select.Option>
          </Select>
          <Upload accept=".csv,.xlsx,.xls" showUploadList={false} beforeUpload={handleImport}>
            <Button icon={<UploadOutlined />}>导入</Button>
          </Upload>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>新增</Button>
        </Space>
      </div>

      <Table columns={columns} dataSource={cases} rowKey="id" loading={loading}
        pagination={{ current: page, pageSize, total, onChange: (p, s) => { setPage(p); setPageSize(s || 50); } }} />

      <Modal title={editingId ? '编辑测评题' : '新增测评题'} open={isModalOpen} onOk={handleOk} onCancel={() => setIsModalOpen(false)} okText="确定" cancelText="取消" width={640}>
        <Form form={form} layout="vertical">
          <Form.Item name="content" label="话术内容" rules={[{ required: true, message: '请输入话术内容' }]}>
            <TextArea rows={4} placeholder="输入测评话术..." />
          </Form.Item>
          <Form.Item name="tag_codes" label="标签">
            <Select mode="multiple" placeholder="选择标签" allowClear>
              {tags.filter(t => t.level === 2).map(t => <Select.Option key={t.tag_code} value={t.tag_code}>{t.tag_name} ({t.tag_code})</Select.Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="risk_point" label="风险点">
            <Input placeholder="风险点描述" />
          </Form.Item>
          <Form.Item name="expected_result" label="预期结果" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="VIOLATION">违规 (VIOLATION)</Select.Option>
              <Select.Option value="COMPLIANT">合规 (COMPLIANT)</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="is_active" label="是否启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default EvalTestCasesPage;

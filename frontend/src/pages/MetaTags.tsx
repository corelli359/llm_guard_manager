import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, InputNumber, Switch, Space, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { MetaTag } from '../types';
import { metaTagsApi } from '../api';

const MetaTagsPage: React.FC = () => {
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  const fetchTags = async () => {
    setLoading(true);
    try {
      const res = await metaTagsApi.getAll();
      setTags(res.data);
    } catch (error) {
      message.error('获取标签列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTags();
  }, []);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    // Default values
    form.setFieldsValue({ level: 2, is_active: true });
    setIsModalOpen(true);
  };

  const handleEdit = (record: MetaTag) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await metaTagsApi.delete(id);
      message.success('标签已删除');
      fetchTags();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await metaTagsApi.update(editingId, values);
        message.success('标签已更新');
      } else {
        await metaTagsApi.create(values);
        message.success('标签已创建');
      }
      setIsModalOpen(false);
      fetchTags();
    } catch (error) {
      // Form validation error or API error
      console.error(error);
    }
  };

  const columns = [
    { title: '标签编码 (Code)', dataIndex: 'tag_code', key: 'tag_code' },
    { title: '标签名称', dataIndex: 'tag_name', key: 'tag_name' },
    { title: '父级编码', dataIndex: 'parent_code', key: 'parent_code' },
    { title: '层级 (Level)', dataIndex: 'level', key: 'level' },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: MetaTag) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定删除该标签吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>标签管理 (Meta Tags)</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增标签
        </Button>
      </div>
      
      <Table 
        columns={columns} 
        dataSource={tags} 
        rowKey="id" 
        loading={loading}
      />

      <Modal 
        title={editingId ? "编辑标签" : "新增标签"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="tag_code" label="标签编码 (Tag Code)" rules={[{ required: true, message: '请输入标签编码' }]}>
            <Input disabled={!!editingId} placeholder="例如：POLITICS" /> 
          </Form.Item>
          <Form.Item name="tag_name" label="标签名称" rules={[{ required: true, message: '请输入标签名称' }]}>
            <Input placeholder="例如：政治敏感" />
          </Form.Item>
          <Form.Item name="parent_code" label="父级编码 (Parent Code)">
            <Input placeholder="可选" />
          </Form.Item>
          <Form.Item name="level" label="层级 (Level)" rules={[{ required: true }]}>
            <InputNumber min={1} />
          </Form.Item>
          <Form.Item name="is_active" label="是否启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default MetaTagsPage;
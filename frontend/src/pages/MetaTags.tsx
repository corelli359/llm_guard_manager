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
      message.error('Failed to fetch tags');
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
      message.success('Tag deleted');
      fetchTags();
    } catch (error) {
      message.error('Failed to delete tag');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await metaTagsApi.update(editingId, values);
        message.success('Tag updated');
      } else {
        await metaTagsApi.create(values);
        message.success('Tag created');
      }
      setIsModalOpen(false);
      fetchTags();
    } catch (error) {
      // Form validation error or API error
      console.error(error);
    }
  };

  const columns = [
    { title: 'Tag Code', dataIndex: 'tag_code', key: 'tag_code' },
    { title: 'Tag Name', dataIndex: 'tag_name', key: 'tag_name' },
    { title: 'Parent Code', dataIndex: 'parent_code', key: 'parent_code' },
    { title: 'Level', dataIndex: 'level', key: 'level' },
    {
      title: 'Active',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: MetaTag) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record.id)}>
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Meta Tags Management</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Add New Tag
        </Button>
      </div>
      
      <Table 
        columns={columns} 
        dataSource={tags} 
        rowKey="id" 
        loading={loading}
      />

      <Modal 
        title={editingId ? "Edit Tag" : "Add New Tag"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="tag_code" label="Tag Code" rules={[{ required: true }]}>
            <Input disabled={!!editingId} /> 
          </Form.Item>
          <Form.Item name="tag_name" label="Tag Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="parent_code" label="Parent Code">
            <Input />
          </Form.Item>
          <Form.Item name="level" label="Level" rules={[{ required: true }]}>
            <InputNumber min={1} />
          </Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default MetaTagsPage;

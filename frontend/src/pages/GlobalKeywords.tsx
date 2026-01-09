import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { GlobalKeyword } from '../types';
import { globalKeywordsApi } from '../api';

const GlobalKeywordsPage: React.FC = () => {
  const [keywords, setKeywords] = useState<GlobalKeyword[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form] = Form.useForm();

  const fetchKeywords = async () => {
    setLoading(true);
    try {
      // Fetching all for simplicity, pagination can be added
      const res = await globalKeywordsApi.getAll(0, 1000);
      setKeywords(res.data);
    } catch (error) {
      message.error('Failed to fetch keywords');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeywords();
  }, []);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({ is_active: true, risk_level: 'High' });
    setIsModalOpen(true);
  };

  const handleEdit = (record: GlobalKeyword) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await globalKeywordsApi.delete(id);
      message.success('Keyword deleted');
      fetchKeywords();
    } catch (error) {
      message.error('Failed to delete keyword');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await globalKeywordsApi.update(editingId, values);
        message.success('Keyword updated');
      } else {
        await globalKeywordsApi.create(values);
        message.success('Keyword created');
      }
      setIsModalOpen(false);
      fetchKeywords();
    } catch (error) {
      console.error(error);
    }
  };

  const columns = [
    { title: 'Keyword', dataIndex: 'keyword', key: 'keyword' },
    { title: 'Tag Code', dataIndex: 'tag_code', key: 'tag_code' },
    { title: 'Risk Level', dataIndex: 'risk_level', key: 'risk_level' },
    {
      title: 'Active',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: GlobalKeyword) => (
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
        <h2>Global Keywords</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Add New Keyword
        </Button>
      </div>

      <Table 
        columns={columns} 
        dataSource={keywords} 
        rowKey="id" 
        loading={loading}
      />

      <Modal 
        title={editingId ? "Edit Keyword" : "Add New Keyword"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="keyword" label="Keyword" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="tag_code" label="Tag Code" rules={[{ required: true }]}>
             <Input /> 
             {/* In a real app, this should be a Select from fetchTags */}
          </Form.Item>
          <Form.Item name="risk_level" label="Risk Level" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="High">High</Select.Option>
              <Select.Option value="Medium">Medium</Select.Option>
              <Select.Option value="Low">Low</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default GlobalKeywordsPage;

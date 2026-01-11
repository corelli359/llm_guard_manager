import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Switch, Space, message, Popconfirm, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { GlobalKeyword, MetaTag } from '../types';
import { globalKeywordsApi, metaTagsApi } from '../api';

const { Search } = Input;
const { Option } = Select;

const GlobalKeywordsPage: React.FC = () => {
  const [keywords, setKeywords] = useState<GlobalKeyword[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [searchText, setSearchText] = useState<string>('');
  const [form] = Form.useForm();

  const fetchKeywords = async (query?: string) => {
    setLoading(true);
    try {
      // Fetching all for simplicity, pagination can be added
      // Passing query for search
      const res = await globalKeywordsApi.getAll(0, 1000, query);
      setKeywords(res.data);
    } catch (error) {
      message.error('获取敏感词列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const res = await metaTagsApi.getAll();
      setTags(res.data);
    } catch (error) {
      message.error('获取标签列表失败');
    }
  };

  useEffect(() => {
    fetchKeywords();
    fetchTags();
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
      message.success('敏感词已删除');
      fetchKeywords(searchText);
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await globalKeywordsApi.update(editingId, values);
        message.success('敏感词已更新');
      } else {
        await globalKeywordsApi.create(values);
        message.success('敏感词已创建');
      }
      setIsModalOpen(false);
      fetchKeywords(searchText);
    } catch (error: any) {
      console.error(error);
      if (error.response && error.response.data && error.response.data.detail) {
        message.error(`操作失败: ${error.response.data.detail}`);
      } else if (error.errorFields) {
         // Form validation error, do nothing
      } else {
        message.error('操作失败，请重试');
      }
    }
  };
  
  const onSearch = (value: string) => {
    setSearchText(value);
    fetchKeywords(value);
  };

  const columns = [
    { title: '敏感词 (Keyword)', dataIndex: 'keyword', key: 'keyword' },
    { title: '关联标签 (Tag)', dataIndex: 'tag_code', key: 'tag_code', render: (text: string) => <Tag color="blue">{text}</Tag> },
    { 
      title: '风险等级', 
      dataIndex: 'risk_level', 
      key: 'risk_level',
      render: (level: string) => {
        let color = 'default';
        if (level === 'High') color = 'red';
        if (level === 'Medium') color = 'orange';
        if (level === 'Low') color = 'green';
        return <Tag color={color}>{level}</Tag>;
      }
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: GlobalKeyword) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定删除该敏感词吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>全局敏感词库 (Global Keywords)</h2>
        <Space>
           <Search placeholder="搜索敏感词..." onSearch={onSearch} enterButton allowClear style={{ width: 300 }} />
           <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
             新增敏感词
           </Button>
        </Space>
      </div>

      <Table 
        columns={columns} 
        dataSource={keywords} 
        rowKey="id" 
        loading={loading}
      />

      <Modal 
        title={editingId ? "编辑敏感词" : "新增敏感词"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="keyword" label="敏感词内容" rules={[{ required: true, message: '请输入敏感词' }]}>
            <Input placeholder="例如：某些敏感词汇" />
          </Form.Item>
          
          <Form.Item name="tag_code" label="关联标签 (Tag Code)" rules={[{ required: true, message: '请选择标签' }]}>
            <Select placeholder="请选择标签" showSearch optionFilterProp="children">
              {tags.map(tag => (
                <Option key={tag.tag_code} value={tag.tag_code}>{tag.tag_name} ({tag.tag_code})</Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item name="risk_level" label="风险等级" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="High">高 (High)</Select.Option>
              <Select.Option value="Medium">中 (Medium)</Select.Option>
              <Select.Option value="Low">低 (Low)</Select.Option>
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

export default GlobalKeywordsPage;

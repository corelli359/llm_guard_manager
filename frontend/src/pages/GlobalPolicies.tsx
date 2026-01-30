import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Select, Switch, Space, message, Popconfirm, Tag, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { RuleGlobalDefault, MetaTag } from '../types';
import { globalPoliciesApi, metaTagsApi } from '../api';

const GlobalPoliciesPage: React.FC = () => {
  const [policies, setPolicies] = useState<RuleGlobalDefault[]>([]);
  const [tags, setTags] = useState<MetaTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [form] = Form.useForm();

  useEffect(() => {
    fetchPolicies();
    fetchTags();
  }, []);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const res = await globalPoliciesApi.getAll();
      setPolicies(res.data);
    } catch (error) {
      message.error('获取全局默认规则失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const res = await metaTagsApi.getAll();
      setTags(res.data.filter((tag: MetaTag) => tag.is_active));
    } catch (error) {
      console.error('Failed to fetch tags', error);
    }
  };

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldsValue({ 
      is_active: true, 
      strategy: 'BLOCK'
    });
    setIsModalOpen(true);
  };

  const handleEdit = (record: RuleGlobalDefault) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await globalPoliciesApi.delete(id);
      message.success('规则已删除');
      fetchPolicies();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        await globalPoliciesApi.update(editingId, values);
        message.success('规则已更新');
      } else {
        await globalPoliciesApi.create(values);
        message.success('规则已创建');
      }
      setIsModalOpen(false);
      fetchPolicies();
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

  const columns = [
    { title: '标签编码', dataIndex: 'tag_code', key: 'tag_code', render: (text: string) => <Tag color="blue">{text}</Tag> },
    { title: '额外条件', dataIndex: 'extra_condition', key: 'extra_condition' },
    { title: '处置策略', dataIndex: 'strategy', key: 'strategy',
      render: (val: string) => {
        let color = 'default';
        let text = val;
        if (val === 'BLOCK') { color = 'red'; text = '拦截 (BLOCK)'; }
        if (val === 'PASS') { color = 'green'; text = '放行 (PASS)'; }
        if (val === 'REWRITE') { color = 'orange'; text = '重写 (REWRITE)'; }
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '是否启用',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => <Switch size="small" checked={active} disabled />
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: RuleGlobalDefault) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定要删除此规则吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>全局默认规则管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增默认规则
        </Button>
      </div>

      <Table 
        columns={columns} 
        dataSource={policies} 
        rowKey="id" 
        loading={loading}
      />

      <Modal 
        title={editingId ? "编辑规则" : "新增规则"} 
        open={isModalOpen} 
        onOk={handleOk} 
        onCancel={() => setIsModalOpen(false)}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="tag_code"
            label="标签编码 (Tag Code)"
            rules={[{ required: true, message: '请选择标签编码' }]}
            help="该默认规则适用的分类标签。"
          >
            <Select
              placeholder="请选择标签"
              showSearch
              optionFilterProp="children"
            >
              {tags.map(tag => (
                <Select.Option key={tag.tag_code} value={tag.tag_code}>
                  {tag.tag_name} ({tag.tag_code})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
                <Form.Item name="strategy" label="处置策略 (Strategy)" rules={[{ required: true }]}>
                    <Select>
                        <Select.Option value="BLOCK">拦截 (BLOCK)</Select.Option>
                        <Select.Option value="PASS">放行 (PASS)</Select.Option>
                        <Select.Option value="REWRITE">重写 (REWRITE)</Select.Option>
                    </Select>
                </Form.Item>
            </Col>
            <Col span={12}>
                <Form.Item 
                    name="extra_condition" 
                    label="额外条件"
                    help="可选。例如特定的模型判定结果。"
                >
                    <Select allowClear placeholder="请选择或输入...">
                        <Select.Option value="safe">safe (安全)</Select.Option>
                        <Select.Option value="unsafe">unsafe (不安全)</Select.Option>
                        <Select.Option value="controversial">controversial (有争议)</Select.Option>
                    </Select>
                </Form.Item>
            </Col>
          </Row>

          <Form.Item name="is_active" label="是否启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default GlobalPoliciesPage;
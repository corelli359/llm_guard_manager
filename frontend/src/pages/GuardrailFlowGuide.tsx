import React from 'react';
import { Button, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title: AntTitle } = Typography;

/* ── 颜色 ── */
const C = {
  indigo: '#6366f1',
  green: '#10b981', greenDk: '#059669',
  amber: '#f59e0b', amberDk: '#d97706',
  red: '#ef4444', purple: '#8b5cf6',
};

/* ── 节点 ── */
const Node: React.FC<{
  t: string; bg?: string; c?: string; w?: number; icon?: string; large?: boolean;
}> = ({ t, bg = C.green, c = '#fff', w = 160, icon, large }) => (
  <div style={{
    width: w, background: bg, color: c, borderRadius: large ? 14 : 10,
    padding: large ? '12px 20px' : '8px 14px', textAlign: 'center', fontWeight: 600,
    fontSize: large ? 16 : 14, lineHeight: 1.5,
    boxShadow: large ? '0 4px 16px rgba(0,0,0,0.15)' : '0 2px 8px rgba(0,0,0,0.1)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
  }}>
    {icon && <span style={{ fontSize: large ? 18 : 15 }}>{icon}</span>}{t}
  </div>
);

/* ── 竖向箭头 ── */
const VArrow: React.FC<{ h?: number; color?: string; label?: string }> = ({
  h = 28, color = '#cbd5e1', label,
}) => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '2px 0' }}>
    {label && <span style={{ fontSize: 11, color: '#94a3b8', marginBottom: -1 }}>{label}</span>}
    <svg width="14" height={h} viewBox={`0 0 14 ${h}`}>
      <line x1="7" y1="0" x2="7" y2={h - 7} stroke={color} strokeWidth="2.5" />
      <polygon points={`2,${h - 7} 12,${h - 7} 7,${h}`} fill={color} />
    </svg>
  </div>
);

/* ── 横向箭头 ── */
const HArrow: React.FC<{ w?: number; label?: string }> = ({ w = 70, label }) => (
  <div style={{
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    margin: '0 4px', flexShrink: 0,
  }}>
    {label && <span style={{ fontSize: 11, color: '#94a3b8', marginBottom: 2, fontWeight: 500 }}>{label}</span>}
    <svg width={w} height="16" viewBox={`0 0 ${w} 16`}>
      <line x1="0" y1="8" x2={w - 8} y2="8" stroke="#cbd5e1" strokeWidth="2.5" />
      <polygon points={`${w - 8},3 ${w - 8},13 ${w},8`} fill="#cbd5e1" />
    </svg>
  </div>
);

/* ── 并行框 ── */
const Parallel: React.FC<{ children: React.ReactNode; borderColor: string; bg: string }> = ({
  children, borderColor, bg,
}) => (
  <div style={{
    display: 'flex', alignItems: 'flex-start', gap: 16,
    padding: '18px 22px 14px', borderRadius: 12,
    border: `2px dashed ${borderColor}70`, background: bg,
    position: 'relative',
  }}>
    <div style={{
      position: 'absolute', top: -10, left: '50%', transform: 'translateX(-50%)',
      fontSize: 11, color: '#475569', background: bg, padding: '1px 12px',
      fontWeight: 700, whiteSpace: 'nowrap', borderRadius: 6,
      border: `1px solid ${borderColor}40`,
    }}>⚡ 并行执行</div>
    {children}
  </div>
);

/* ── 决策结果行 ── */
const Decisions: React.FC<{ items: { t: string; bg: string; c: string; icon: string }[] }> = ({ items }) => (
  <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'nowrap' }}>
    {items.map(({ t, bg, c, icon }) => (
      <div key={t} style={{
        background: bg, color: c, borderRadius: 8,
        padding: '5px 10px', fontWeight: 600, fontSize: 12,
        display: 'flex', alignItems: 'center', gap: 3,
        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
        whiteSpace: 'nowrap',
      }}>
        <span>{icon}</span>{t}
      </div>
    ))}
  </div>
);

/* ── 区域卡片 ── */
const GuardCard: React.FC<{
  badge: string; badgeColor: string; borderColor: string; bg: string;
  subtitle: string; children: React.ReactNode;
}> = ({ badge, badgeColor, borderColor, bg, subtitle, children }) => (
  <div style={{
    position: 'relative', flex: 1, minWidth: 0,
    background: bg, border: `2px solid ${borderColor}`,
    borderRadius: 16, padding: '36px 28px 22px',
    boxShadow: `0 2px 12px ${borderColor}15`,
  }}>
    <div style={{
      position: 'absolute', top: -14, left: 20,
      background: `linear-gradient(135deg, ${badgeColor}, ${badgeColor}cc)`,
      color: '#fff', fontSize: 13, fontWeight: 700,
      padding: '4px 18px', borderRadius: 20, letterSpacing: 2,
      boxShadow: `0 2px 8px ${badgeColor}40`,
    }}>{badge}</div>
    <div style={{
      position: 'absolute', top: -13, right: 20,
      fontSize: 11, color: '#94a3b8', background: bg, padding: '3px 10px',
      borderRadius: 10, border: `1px solid ${borderColor}40`, fontWeight: 500,
    }}>{subtitle}</div>
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
      {children}
    </div>
  </div>
);

/* ── 主组件 ── */
const GuardrailFlowGuide: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '20px 32px' }}>
      {/* 顶栏 */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginBottom: 20,
      }}>
        <div>
          <AntTitle level={3} style={{ margin: 0 }}>安全围栏防护流程</AntTitle>
          <span style={{ fontSize: 14, color: '#94a3b8' }}>输入 / 输出双层防护架构</span>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/playground')}>
          返回试验场
        </Button>
      </div>

      {/* 流程主体 */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 0, flexWrap: 'nowrap',
        background: '#f8fafc', borderRadius: 18, padding: '36px 28px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 8px rgba(0,0,0,0.04)',
      }}>
        {/* 起点 */}
        <div style={{ flexShrink: 0 }}>
          <Node t="用户输入" bg={`linear-gradient(135deg,${C.indigo},${C.purple})`} w={88} icon="💬" />
        </div>

        <HArrow w={56} />

        {/* ===== 输入围栏 ===== */}
        <GuardCard
          badge="输入围栏" badgeColor={C.green} borderColor={C.green}
          bg="#f0fdf4" subtitle="Input Guard"
        >
          <Node t="字符编码审查" bg={C.green} w={160} icon="🔍" />
          <VArrow color={C.green} />
          <Parallel borderColor={C.green} bg="#ecfdf5">
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Node t="敏感词过滤" bg={C.green} w={140} icon="📝" />
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 4, lineHeight: 1.3, textAlign: 'center' }}>
                全局词库 + 场景自定义
              </div>
            </div>
            <Node t="安全模型过滤" bg={C.green} w={140} icon="🤖" />
          </Parallel>
          <VArrow color={C.green} />
          <Node t="规则引擎" bg={C.greenDk} w={160} icon="⚙️" />
          <VArrow color={C.green} />
          <Decisions items={[
            { t: '引导识别与改写', bg: '#fef3c7', c: '#92400e', icon: '✏️' },
            { t: '放行', bg: '#dcfce7', c: '#166534', icon: '✅' },
            { t: '拒答', bg: '#fee2e2', c: '#991b1b', icon: '🚫' },
            { t: '转人工', bg: '#ede9fe', c: '#5b21b6', icon: '👤' },
          ]} />
        </GuardCard>

        <HArrow w={56} label="放行后" />

        {/* ===== 输出围栏 ===== */}
        <GuardCard
          badge="输出围栏" badgeColor={C.amber} borderColor={C.amber}
          bg="#fffbeb" subtitle="Output Guard"
        >
          <Node t="大模型生成" bg={C.amber} w={160} icon="🧠" />
          <VArrow color={C.amber} />
          <Parallel borderColor={C.amber} bg="#fef9ee">
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Node t="敏感词过滤" bg={C.amber} w={140} icon="📝" />
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 4, lineHeight: 1.3, textAlign: 'center' }}>
                全局 + 场景自定义 · 实时
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Node t="安全模型过滤" bg={C.amber} w={140} icon="🤖" />
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>滑窗旁路</div>
            </div>
          </Parallel>
          <VArrow color={C.amber} />
          <Node t="规则引擎" bg={C.amberDk} w={160} icon="⚙️" />
          <VArrow color={C.amber} />
          <Decisions items={[
            { t: '安全输出', bg: '#dcfce7', c: '#166534', icon: '✅' },
            { t: '中断输出', bg: '#fee2e2', c: '#991b1b', icon: '⛔' },
            { t: '安全代答', bg: '#fef3c7', c: '#92400e', icon: '🔄' },
          ]} />
        </GuardCard>

        <HArrow w={56} />

        {/* 终点 */}
        <div style={{ flexShrink: 0 }}>
          <Node t="模型输出" bg={`linear-gradient(135deg,${C.indigo},${C.purple})`} w={88} icon="✨" />
        </div>
      </div>

      {/* 图例 */}
      <div style={{
        display: 'flex', gap: 28, justifyContent: 'center', flexWrap: 'wrap',
        marginTop: 16, padding: '10px 20px', background: '#f1f5f9',
        borderRadius: 10, fontSize: 13, color: '#64748b',
      }}>
        {[
          { s: '通过 = 0', c: '#22c55e' },
          { s: '改写 = 50', c: '#eab308' },
          { s: '拒答 = 100', c: '#ef4444' },
          { s: '转人工 = 1000', c: '#8b5cf6' },
        ].map(({ s, c }) => (
          <span key={s} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{
              width: 12, height: 12, borderRadius: 3, background: c,
              display: 'inline-block', boxShadow: `0 1px 4px ${c}40`,
            }} />
            {s}
          </span>
        ))}
      </div>
    </div>
  );
};

export default GuardrailFlowGuide;

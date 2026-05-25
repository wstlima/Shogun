import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import type { DragEvent } from 'react';
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
  Handle,
  Position,
  MarkerType,
  useReactFlow,
  ReactFlowProvider,
  BaseEdge,
  getSmoothStepPath,
  EdgeLabelRenderer,
} from '@xyflow/react';
import type {
  Connection,
  Node,
  Edge,
  NodeTypes,
  EdgeTypes,
  EdgeProps,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Save,
  Plus,
  Trash2,
  Copy,
  Play,
  ChevronLeft,
  X,
  Users,
  Shield,
  GitBranch,
  LogIn,
  LogOut,
  Loader2,
  Zap,
  Clock,
  RefreshCw,
  Search,
  MoreVertical,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  History,
  StopCircle,
  Globe,
} from 'lucide-react';
import axios from 'axios';
import { cn } from '../lib/utils';


// ═══════════════════════════════════════════════════════════════
// TYPE DEFINITIONS
// ═══════════════════════════════════════════════════════════════

interface AgentFlowData {
  id: string;
  name: string;
  description: string | null;
  status: string;
  trigger_type: string;
  schedule_config: Record<string, any>;
  viewport: { x: number; y: number; zoom: number };
  nodes: FlowNodeData[];
  edges: FlowEdgeData[];
  created_at: string;
  updated_at: string;
}

interface FlowNodeData {
  id: string;
  flow_id: string;
  node_type: string;
  label: string;
  position_x: number;
  position_y: number;
  config: Record<string, any>;
}

interface FlowEdgeData {
  id: string;
  flow_id: string;
  source_node_id: string;
  target_node_id: string;
  source_handle: string | null;
  target_handle: string | null;
  label: string | null;
  edge_type: string;
  config: Record<string, any>;
}

interface FlowListItem {
  id: string;
  name: string;
  description: string | null;
  status: string;
  trigger_type: string;
  created_at: string;
  updated_at: string;
}


// ═══════════════════════════════════════════════════════════════
// NODE PALETTE — card types available for dragging
// ═══════════════════════════════════════════════════════════════

const NODE_PALETTE = [
  { type: 'samurai',         label: 'Samurai',          icon: Users,     color: '#d4a017', desc: 'Task worker / sub-agent' },
  { type: 'shogun_approval', label: 'Shogun Approval',  icon: Shield,    color: '#4a8cc7', desc: 'Approval gate' },
  { type: 'logic',           label: 'Logic / Decision', icon: GitBranch, color: '#a78bfa', desc: 'Branching logic' },
  { type: 'input',           label: 'Input',            icon: LogIn,     color: '#22c55e', desc: 'Workflow start point' },
  { type: 'output',          label: 'Output',           icon: LogOut,    color: '#f97316', desc: 'Final delivery' },
  { type: 'mado_browser',    label: 'Mado Browser',     icon: Globe,     color: '#06b6d4', desc: 'Browser automation' },
] as const;


// ═══════════════════════════════════════════════════════════════
// CUSTOM NODES
// ═══════════════════════════════════════════════════════════════

const nodeColors: Record<string, string> = {
  samurai: '#d4a017',
  shogun_approval: '#4a8cc7',
  logic: '#a78bfa',
  input: '#22c55e',
  output: '#f97316',
  mado_browser: '#06b6d4',
};

const nodeIcons: Record<string, React.ElementType> = {
  samurai: Users,
  shogun_approval: Shield,
  logic: GitBranch,
  input: LogIn,
  output: LogOut,
  mado_browser: Globe,
};

function FlowNode({ data, selected, type }: { data: Record<string, any>; selected: boolean; type: string }) {
  const color = nodeColors[type] || '#d4a017';
  const Icon = nodeIcons[type] || Users;
  const config: Record<string, any> = data.config || {};

  return (
    <div
      className={cn(
        "relative min-w-[200px] max-w-[260px] rounded-lg border transition-all duration-200",
        selected
          ? "ring-2 ring-offset-1 ring-offset-[#0a0e1a] shadow-lg"
          : "shadow-md hover:shadow-lg"
      )}
      style={{
        background: '#0e1225',
        borderColor: selected ? color : '#1a2040',
        ...(selected ? { ringColor: color } : {}),
      }}
    >
      {/* Top accent bar */}
      <div className="h-1 rounded-t-lg" style={{ background: color }} />

      {/* Header */}
      <div className="px-3 py-2 flex items-center gap-2 border-b" style={{ borderColor: '#1a204060' }}>
        <div
          className="w-6 h-6 rounded flex items-center justify-center shrink-0"
          style={{ background: `${color}15`, border: `1px solid ${color}30` }}
        >
          <Icon className="w-3.5 h-3.5" style={{ color }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[11px] font-bold text-[#c8d0d8] truncate">{data.label}</div>
          <div className="text-[8px] font-bold uppercase tracking-widest" style={{ color: `${color}90` }}>
            {type.replace('_', ' ')}
          </div>
        </div>
      </div>

      {/* Body — type-specific preview */}
      <div className="px-3 py-2 space-y-1">
        {type === 'samurai' && (
          <>
            {config.task_description && (
              <p className="text-[9px] text-[#7a8899] line-clamp-2">{config.task_description}</p>
            )}
            {config.routing_profile_name && (
              <div className="flex items-center gap-1">
                <Zap className="w-2.5 h-2.5 text-[#d4a017]/70" />
                <span className="text-[8px] font-bold text-[#d4a017]/80">{config.routing_profile_name}</span>
              </div>
            )}
            {!config.task_description && !config.routing_profile_name && (
              <p className="text-[9px] text-[#7a8899]/50 italic">Configure task...</p>
            )}
          </>
        )}
        {type === 'shogun_approval' && (
          <>
            <div className="flex items-center gap-1">
              <Shield className="w-2.5 h-2.5 text-[#4a8cc7]/70" />
              <span className="text-[8px] font-bold text-[#4a8cc7]/80 uppercase">
                {config.approval_mode || 'manual'} approval
              </span>
            </div>
            {config.confidence_threshold && (
              <span className="text-[8px] text-[#7a8899]">
                Threshold: {config.confidence_threshold}%
              </span>
            )}
          </>
        )}
        {type === 'logic' && (
          <p className="text-[9px] text-[#a78bfa]/80 font-mono">
            {config.condition_expression || 'IF condition → ...'}
          </p>
        )}
        {type === 'input' && (
          <div className="flex items-center gap-1">
            <span className="text-[8px] font-bold text-[#22c55e]/80 uppercase">
              {config.input_type || 'manual'} trigger
            </span>
          </div>
        )}
        {type === 'output' && (
          <div className="flex items-center gap-1">
            <span className="text-[8px] font-bold text-[#f97316]/80 uppercase">
              {config.output_type || 'artifact'}
            </span>
          </div>
        )}
        {type === 'mado_browser' && (
          <>
            <div className="flex items-center gap-1">
              <Globe className="w-2.5 h-2.5 text-[#06b6d4]/70" />
              <span className="text-[8px] font-bold text-[#06b6d4]/80 uppercase">
                {config.action || 'navigate'}
              </span>
            </div>
            {config.url && (
              <p className="text-[9px] text-[#7a8899] truncate">{config.url}</p>
            )}
          </>
        )}
      </div>

      {/* Handles */}
      {type !== 'input' && (
        <Handle
          type="target"
          position={Position.Left}
          className="!w-2.5 !h-2.5 !border-2 !rounded-full !bg-[#0a0e1a]"
          style={{ borderColor: color }}
        />
      )}
      {type !== 'output' && (
        <Handle
          type="source"
          position={Position.Right}
          className="!w-2.5 !h-2.5 !border-2 !rounded-full !bg-[#0a0e1a]"
          style={{ borderColor: color }}
        />
      )}
      {/* Logic nodes get extra handles for branches */}
      {type === 'logic' && (
        <>
          <Handle
            type="source"
            position={Position.Bottom}
            id="false"
            className="!w-2.5 !h-2.5 !border-2 !rounded-full !bg-[#0a0e1a]"
            style={{ borderColor: '#ef4444' }}
          />
        </>
      )}

      {/* Execution status overlay */}
      {data.execution_status && data.execution_status !== 'pending' && (
        <div className="absolute -top-1 -right-1 z-10">
          {data.execution_status === 'running' && (
            <div className="w-5 h-5 rounded-full bg-[#4a8cc7] flex items-center justify-center animate-pulse shadow-[0_0_8px_rgba(74,140,199,0.5)]">
              <Loader2 className="w-3 h-3 text-white animate-spin" />
            </div>
          )}
          {data.execution_status === 'completed' && (
            <div className="w-5 h-5 rounded-full bg-[#22c55e] flex items-center justify-center shadow-[0_0_8px_rgba(34,197,94,0.4)]">
              <CheckCircle2 className="w-3 h-3 text-white" />
            </div>
          )}
          {data.execution_status === 'failed' && (
            <div className="w-5 h-5 rounded-full bg-[#ef4444] flex items-center justify-center shadow-[0_0_8px_rgba(239,68,68,0.4)]">
              <XCircle className="w-3 h-3 text-white" />
            </div>
          )}
          {data.execution_status === 'skipped' && (
            <div className="w-5 h-5 rounded-full bg-[#7a8899] flex items-center justify-center">
              <AlertTriangle className="w-3 h-3 text-white" />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Register custom node types
const nodeTypes: NodeTypes = {
  samurai: FlowNode,
  shogun_approval: FlowNode,
  logic: FlowNode,
  input: FlowNode,
  output: FlowNode,
  mado_browser: FlowNode,
};


// ═══════════════════════════════════════════════════════════════
// CUSTOM EDGE
// ═══════════════════════════════════════════════════════════════

function CustomEdge({
  id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition,
  data, markerEnd, style, selected,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition,
    borderRadius: 12,
  });

  const edgeColor = data?.edge_type === 'success' ? '#22c55e'
    : data?.edge_type === 'failure' ? '#ef4444'
    : data?.edge_type === 'conditional' ? '#a78bfa'
    : '#4a8cc7';

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          stroke: selected ? '#d4a017' : edgeColor,
          strokeWidth: selected ? 2.5 : 1.5,
          opacity: selected ? 1 : 0.7,
        }}
      />
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            className="absolute text-[8px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border pointer-events-all"
            style={{
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              background: '#0e1225',
              borderColor: edgeColor + '40',
              color: edgeColor,
            }}
          >
            {data.label as string}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

const edgeTypes: EdgeTypes = {
  custom: CustomEdge,
};


// ═══════════════════════════════════════════════════════════════
// NODE INSPECTOR PANEL
// ═══════════════════════════════════════════════════════════════

function NodeInspector({
  node,
  onUpdate,
  onClose,
  agents,
  routingProfiles,
}: {
  node: Node;
  onUpdate: (id: string, data: any) => void;
  onClose: () => void;
  agents: any[];
  routingProfiles: any[];
}) {
  const nodeType = node.type || 'samurai';
  const color = nodeColors[nodeType] || '#d4a017';
  const Icon = nodeIcons[nodeType] || Users;
  const config: Record<string, any> = (node.data as Record<string, any>)?.config || {};

  const updateConfig = (key: string, value: any) => {
    onUpdate(node.id, {
      ...node.data,
      config: { ...config, [key]: value },
    });
  };

  const updateLabel = (label: string) => {
    onUpdate(node.id, { ...node.data, label });
  };

  return (
    <div className="w-[300px] bg-[#050508] border-l border-[#1a2040] h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-[#1a2040] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: `${color}15`, border: `1px solid ${color}30` }}
          >
            <Icon className="w-4 h-4" style={{ color }} />
          </div>
          <div>
            <h3 className="text-xs font-bold text-[#c8d0d8]">Node Properties</h3>
            <span className="text-[8px] font-bold uppercase tracking-widest" style={{ color }}>
              {nodeType.replace('_', ' ')}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-[#1a2040] text-[#7a8899] hover:text-[#c8d0d8] rounded-lg transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Label */}
        <div className="space-y-1.5">
          <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Label</label>
          <input
            type="text"
            value={((node.data as Record<string, any>)?.label as string) || ''}
            onChange={(e) => updateLabel(e.target.value)}
            className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#4a8cc7] transition-colors outline-none"
          />
        </div>

        {/* Samurai-specific fields */}
        {nodeType === 'samurai' && (
          <>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Samurai Agent</label>
              <select
                value={config.agent_id || ''}
                onChange={(e) => updateConfig('agent_id', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none cursor-pointer"
              >
                <option value="">Select agent...</option>
                {agents.map((a: any) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Task Description</label>
              <textarea
                value={config.task_description || ''}
                onChange={(e) => updateConfig('task_description', e.target.value)}
                rows={3}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none resize-none"
                placeholder="Describe what this Samurai should do..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Expected Output</label>
              <input
                type="text"
                value={config.expected_output || ''}
                onChange={(e) => updateConfig('expected_output', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none"
                placeholder="e.g., JSON report, markdown summary..."
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest flex items-center gap-1">
                <Zap className="w-3 h-3 text-[#d4a017]/70" /> Routing Profile
              </label>
              <select
                value={config.routing_profile_id || ''}
                onChange={(e) => updateConfig('routing_profile_id', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none cursor-pointer"
              >
                <option value="">System default</option>
                {routingProfiles.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Timeout (s)</label>
                <input
                  type="number"
                  value={config.timeout || 300}
                  onChange={(e) => updateConfig('timeout', parseInt(e.target.value))}
                  className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Retries</label>
                <input
                  type="number"
                  value={config.retry_count || 0}
                  onChange={(e) => updateConfig('retry_count', parseInt(e.target.value))}
                  min={0}
                  max={5}
                  className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">On Failure</label>
              <select
                value={config.failure_action || 'stop'}
                onChange={(e) => updateConfig('failure_action', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none cursor-pointer"
              >
                <option value="stop">Stop workflow</option>
                <option value="retry">Retry</option>
                <option value="skip">Skip and continue</option>
                <option value="escalate">Escalate to Shogun</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Context Injection</label>
              <textarea
                value={config.context_injection || ''}
                onChange={(e) => updateConfig('context_injection', e.target.value)}
                rows={2}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none resize-none"
                placeholder="Additional context to inject..."
              />
            </div>
          </>
        )}

        {/* Shogun Approval fields */}
        {nodeType === 'shogun_approval' && (
          <>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Approval Mode</label>
              <select
                value={config.approval_mode || 'manual'}
                onChange={(e) => updateConfig('approval_mode', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#4a8cc7] transition-colors outline-none cursor-pointer"
              >
                <option value="manual">Manual Human Approval</option>
                <option value="ai_assisted">AI-Assisted Approval</option>
                <option value="policy_based">Policy-Based Approval</option>
                <option value="confidence_threshold">Confidence Threshold</option>
              </select>
            </div>

            {config.approval_mode === 'confidence_threshold' && (
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">
                  Confidence Threshold (%)
                </label>
                <input
                  type="number"
                  value={config.confidence_threshold || 85}
                  onChange={(e) => updateConfig('confidence_threshold', parseInt(e.target.value))}
                  min={0}
                  max={100}
                  className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#4a8cc7] transition-colors outline-none"
                />
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Escalation Action</label>
              <select
                value={config.escalation_action || 'notify'}
                onChange={(e) => updateConfig('escalation_action', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#4a8cc7] transition-colors outline-none cursor-pointer"
              >
                <option value="notify">Notify operator</option>
                <option value="block">Block until manual review</option>
                <option value="reroute">Reroute for revision</option>
                <option value="stop">Stop workflow</option>
              </select>
            </div>
          </>
        )}

        {/* Logic/Decision fields */}
        {nodeType === 'logic' && (
          <>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Condition Expression</label>
              <textarea
                value={config.condition_expression || ''}
                onChange={(e) => updateConfig('condition_expression', e.target.value)}
                rows={3}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-[10px] text-[#a78bfa] font-mono focus:border-[#a78bfa] transition-colors outline-none resize-none"
                placeholder="e.g., confidence > 85%"
              />
            </div>
            <div className="p-2.5 bg-[#a78bfa]/5 border border-[#a78bfa]/20 rounded-lg">
              <p className="text-[8px] text-[#a78bfa]/80">
                <strong>Right handle →</strong> TRUE branch<br />
                <strong>Bottom handle ↓</strong> FALSE branch
              </p>
            </div>
          </>
        )}

        {/* Input fields */}
        {nodeType === 'input' && (
          <>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Input Type</label>
              <select
                value={config.input_type || 'manual'}
                onChange={(e) => updateConfig('input_type', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#22c55e] transition-colors outline-none cursor-pointer"
              >
                <option value="manual">Manual Input</option>
                <option value="document">Document Upload</option>
                <option value="api">API Trigger</option>
                <option value="scheduled">Scheduled Trigger</option>
                <option value="event">Event-Based Trigger</option>
                <option value="nexus">Nexus Task</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Description</label>
              <textarea
                value={config.description || ''}
                onChange={(e) => updateConfig('description', e.target.value)}
                rows={2}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#22c55e] transition-colors outline-none resize-none"
                placeholder="Describe the input..."
              />
            </div>
          </>
        )}

        {/* Output fields */}
        {nodeType === 'output' && (
          <>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Output Type</label>
              <select
                value={config.output_type || 'artifact'}
                onChange={(e) => updateConfig('output_type', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#f97316] transition-colors outline-none cursor-pointer"
              >
                <option value="artifact">Artifact / Report</option>
                <option value="export">Export File</option>
                <option value="api">API Response</option>
                <option value="notification">Notification</option>
                <option value="memory">Store in Memory</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Format</label>
              <select
                value={config.format || 'markdown'}
                onChange={(e) => updateConfig('format', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#f97316] transition-colors outline-none cursor-pointer"
              >
                <option value="markdown">Markdown</option>
                <option value="json">JSON</option>
                <option value="html">HTML</option>
                <option value="plain">Plain Text</option>
              </select>
            </div>
          </>
        )}

        {/* Mado Browser fields */}
        {nodeType === 'mado_browser' && (
          <>
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Action</label>
              <select
                value={config.action || 'navigate'}
                onChange={(e) => updateConfig('action', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
              >
                <option value="navigate">Navigate to URL</option>
                <option value="extract_content">Extract Content</option>
                <option value="screenshot">Take Screenshot</option>
                <option value="fill_form">Fill Form</option>
                <option value="click">Click Element</option>
                <option value="execute_js">Execute JavaScript</option>
                <option value="wait_for">Wait for Element</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">URL</label>
              <input
                type="text"
                value={config.url || ''}
                onChange={(e) => updateConfig('url', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none"
                placeholder="https://example.com"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">CSS Selector</label>
              <input
                type="text"
                value={config.selector || ''}
                onChange={(e) => updateConfig('selector', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-[10px] text-[#06b6d4] font-mono focus:border-[#06b6d4] transition-colors outline-none"
                placeholder="e.g., .main-content, #article, table"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Session Name</label>
              <input
                type="text"
                value={config.session_name || 'flow_browser'}
                onChange={(e) => updateConfig('session_name', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none"
                placeholder="flow_browser"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Browser Mode</label>
              <select
                value={config.browser_mode || 'headless'}
                onChange={(e) => updateConfig('browser_mode', e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
              >
                <option value="headless">Headless</option>
                <option value="visible">Visible</option>
              </select>
            </div>

            {config.action === 'extract_content' && (
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Extract Type</label>
                <select
                  value={config.extract_type || 'text'}
                  onChange={(e) => updateConfig('extract_type', e.target.value)}
                  className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
                >
                  <option value="text">Text</option>
                  <option value="html">HTML</option>
                  <option value="inner_text">Inner Text</option>
                </select>
              </div>
            )}

            {config.action === 'execute_js' && (
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">JavaScript</label>
                <textarea
                  value={config.script || ''}
                  onChange={(e) => updateConfig('script', e.target.value)}
                  rows={4}
                  className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-[10px] text-[#06b6d4] font-mono focus:border-[#06b6d4] transition-colors outline-none resize-none"
                  placeholder="document.title"
                />
              </div>
            )}

            {config.action === 'wait_for' && (
              <div className="space-y-1.5">
                <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Timeout (ms)</label>
                <input
                  type="number"
                  value={config.timeout || 10000}
                  onChange={(e) => updateConfig('timeout', parseInt(e.target.value))}
                  className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none"
                />
              </div>
            )}

            <div className="p-2.5 bg-[#06b6d4]/5 border border-[#06b6d4]/20 rounded-lg">
              <p className="text-[8px] text-[#06b6d4]/80">
                <strong>Mado 窓</strong> — Browser actions are governed by the Torii security posture.
                Domain allowlists and session limits apply.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════
// MAIN CANVAS COMPONENT (wrapped in ReactFlowProvider externally)
// ═══════════════════════════════════════════════════════════════

function AgentFlowCanvas({
  flow,
  onBack,
  onFlowUpdate: _onFlowUpdate,
  agents,
  routingProfiles,
}: {
  flow: AgentFlowData;
  onBack: () => void;
  onFlowUpdate: () => void;
  agents: any[];
  routingProfiles: any[];
}) {
  void _onFlowUpdate; // reserved for Phase 2 execution engine
  const reactFlowInstance = useReactFlow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Convert backend data to React Flow format
  const initialNodes: Node[] = useMemo(() =>
    (flow.nodes || []).map((n) => ({
      id: n.id,
      type: n.node_type,
      position: { x: n.position_x, y: n.position_y },
      data: { label: n.label, config: n.config },
    })),
    [flow.id]
  );

  const initialEdges: Edge[] = useMemo(() =>
    (flow.edges || []).map((e) => ({
      id: e.id,
      source: e.source_node_id,
      target: e.target_node_id,
      sourceHandle: e.source_handle,
      targetHandle: e.target_handle,
      type: 'custom',
      data: { label: e.label, edge_type: e.edge_type },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#4a8cc7', width: 16, height: 16 },
    })),
    [flow.id]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [flowName, setFlowName] = useState(flow.name);
  const [editingName, setEditingName] = useState(false);

  // ── Execution state ──────────────────────────────────────
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<string | null>(null);
  const [nodeStates, setNodeStates] = useState<Record<string, any>>({});
  const [executing, setExecuting] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [runHistory, setRunHistory] = useState<any[]>([]);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Track changes
  useEffect(() => { setDirty(true); }, [nodes, edges]);

  // ── Poll active run status ───────────────────────────────
  useEffect(() => {
    if (!activeRunId) return;
    const poll = async () => {
      try {
        const resp = await axios.get(`/api/v1/agent-flows/runs/${activeRunId}`);
        const run = resp.data?.data;
        if (run) {
          setRunStatus(run.status);
          setNodeStates(run.node_states || {});
          // Apply node status overlays
          setNodes((nds) =>
            nds.map((n) => {
              const ns = run.node_states?.[n.id];
              return {
                ...n,
                data: {
                  ...n.data,
                  execution_status: ns?.status || null,
                },
              };
            })
          );
          if (['completed', 'failed', 'cancelled'].includes(run.status)) {
            setActiveRunId(null);
            setExecuting(false);
            if (pollRef.current) clearInterval(pollRef.current);
          }
        }
      } catch {
        // ignore polling errors
      }
    };
    poll(); // Immediate first poll
    pollRef.current = setInterval(poll, 1500);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [activeRunId, setNodes]);


  // Handle new connections
  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge({
      ...params,
      type: 'custom',
      data: { label: null, edge_type: 'default' },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#4a8cc7', width: 16, height: 16 },
    }, eds));
  }, [setEdges]);

  // Handle node selection
  const onNodeClick = useCallback((_: any, node: Node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Update node data from inspector
  const onNodeDataUpdate = useCallback((nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((n) => (n.id === nodeId ? { ...n, data: newData } : n))
    );
    setSelectedNode((prev) => prev && prev.id === nodeId ? { ...prev, data: newData } : prev);
  }, [setNodes]);

  // Drag-and-drop from palette
  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();
      const nodeType = event.dataTransfer.getData('application/agentflow-node-type');
      if (!nodeType) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const paletteItem = NODE_PALETTE.find((p) => p.type === nodeType);
      const newNode: Node = {
        id: `node-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        type: nodeType,
        position,
        data: {
          label: paletteItem?.label || 'New Node',
          config: {},
        },
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [reactFlowInstance, setNodes]
  );

  // Delete selected nodes/edges
  const onDeleteSelected = useCallback(() => {
    setNodes((nds) => nds.filter((n) => !n.selected));
    setEdges((eds) => eds.filter((e) => !e.selected));
    setSelectedNode(null);
  }, [setNodes, setEdges]);

  // Save flow
  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      // Update flow name if changed
      if (flowName !== flow.name) {
        await axios.patch(`/api/v1/agent-flows/${flow.id}`, { name: flowName });
      }

      // Build graph payload
      const viewport = reactFlowInstance.getViewport();
      const graphPayload = {
        viewport: { x: viewport.x, y: viewport.y, zoom: viewport.zoom },
        nodes: nodes.map((n) => ({
          id: n.id,
          node_type: n.type || 'samurai',
          label: n.data?.label || 'Untitled',
          position_x: n.position.x,
          position_y: n.position.y,
          config: n.data?.config || {},
        })),
        edges: edges.map((e) => ({
          id: e.id,
          source_node_id: e.source,
          target_node_id: e.target,
          source_handle: e.sourceHandle || null,
          target_handle: e.targetHandle || null,
          label: e.data?.label || null,
          edge_type: e.data?.edge_type || 'default',
          config: e.data?.config || {},
        })),
      };

      await axios.put(`/api/v1/agent-flows/${flow.id}/graph`, graphPayload);
      setDirty(false);
    } catch (err) {
      console.error('Failed to save flow:', err);
    } finally {
      setSaving(false);
    }
  }, [flow.id, flow.name, flowName, nodes, edges, reactFlowInstance]);

  // ── Trigger run ──────────────────────────────────────────
  const handleRun = useCallback(async () => {
    if (executing) return;
    // Auto-save before running
    if (dirty) await handleSave();
    setExecuting(true);
    setRunStatus('pending');
    // Clear previous execution overlays
    setNodes((nds) =>
      nds.map((n) => ({ ...n, data: { ...n.data, execution_status: null } }))
    );
    try {
      const resp = await axios.post(`/api/v1/agent-flows/${flow.id}/run`);
      const runId = resp.data?.data?.run_id;
      if (runId) {
        setActiveRunId(runId);
      }
    } catch (err) {
      console.error('Failed to start flow run:', err);
      setExecuting(false);
      setRunStatus(null);
    }
  }, [executing, dirty, handleSave, flow.id, setNodes]);

  // ── Cancel run ───────────────────────────────────────────
  const handleCancel = useCallback(async () => {
    if (!activeRunId) return;
    try {
      await axios.post(`/api/v1/agent-flows/runs/${activeRunId}/cancel`);
      setActiveRunId(null);
      setExecuting(false);
      setRunStatus('cancelled');
    } catch {
      // ignore
    }
  }, [activeRunId]);

  // ── Fetch run history ────────────────────────────────────
  const fetchHistory = useCallback(async () => {
    try {
      const resp = await axios.get(`/api/v1/agent-flows/${flow.id}/runs?limit=20`);
      setRunHistory(resp.data?.data || []);
    } catch {
      // ignore
    }
  }, [flow.id]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA' || document.activeElement?.tagName === 'SELECT') return;
        onDeleteSelected();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [handleSave, onDeleteSelected]);

  // Find the actual selected node object for inspector
  const inspectorNode = selectedNode ? nodes.find((n) => n.id === selectedNode.id) || selectedNode : null;

  return (
    <div className="flex h-[calc(100vh-120px)] rounded-lg overflow-hidden border border-[#1a2040]">
      {/* Canvas */}
      <div className="flex-1 flex flex-col bg-[#060810]">
        {/* Toolbar */}
        <div className="flex items-center justify-between px-3 py-2 bg-[#0a0e1a] border-b border-[#1a2040]">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-1.5 hover:bg-[#1a2040] text-[#7a8899] hover:text-[#c8d0d8] rounded-lg transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <div className="h-5 w-px bg-[#1a2040]" />

            {editingName ? (
              <input
                autoFocus
                type="text"
                value={flowName}
                onChange={(e) => setFlowName(e.target.value)}
                onBlur={() => setEditingName(false)}
                onKeyDown={(e) => e.key === 'Enter' && setEditingName(false)}
                className="bg-[#0e1225] border border-[#d4a017]/40 rounded px-2 py-1 text-sm font-bold text-[#d4a017] outline-none"
              />
            ) : (
              <button
                onClick={() => setEditingName(true)}
                className="text-sm font-bold text-[#d4a017] hover:text-[#d4a017]/80 transition-colors"
              >
                {flowName}
              </button>
            )}

            <span className={cn(
              "text-[8px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border",
              flow.status === 'active'
                ? "text-green-400 bg-green-500/10 border-green-500/20"
                : flow.status === 'paused'
                  ? "text-[#4a8cc7] bg-[#4a8cc7]/10 border-[#4a8cc7]/20"
                  : "text-[#7a8899] bg-[#7a8899]/10 border-[#7a8899]/20"
            )}>
              {flow.status}
            </span>

            {dirty && (
              <span className="text-[8px] text-[#d4a017]/60 font-bold uppercase tracking-widest animate-pulse">
                Unsaved
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Node palette (inline drag buttons) */}
            <div className="flex items-center gap-1 mr-2">
              {NODE_PALETTE.map((item) => {
                const PIcon = item.icon;
                return (
                  <div
                    key={item.type}
                    draggable
                    onDragStart={(e) => {
                      e.dataTransfer.setData('application/agentflow-node-type', item.type);
                      e.dataTransfer.effectAllowed = 'move';
                    }}
                    className="flex items-center gap-1.5 px-2 py-1.5 bg-[#0e1225] border border-[#1a2040] rounded-md cursor-grab active:cursor-grabbing hover:border-[#2a3060] transition-colors group"
                    title={`Drag to add ${item.label}`}
                  >
                    <PIcon className="w-3 h-3" style={{ color: item.color }} />
                    <span className="text-[9px] font-bold text-[#7a8899] group-hover:text-[#c8d0d8] hidden xl:inline">
                      {item.label}
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="h-5 w-px bg-[#1a2040]" />

            <button
              onClick={handleSave}
              disabled={saving}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all",
                saving
                  ? "bg-[#7a8899]/20 text-[#7a8899] cursor-wait"
                  : dirty
                    ? "bg-[#d4a017] text-black hover:bg-[#d4a017]/90 shadow-[0_0_12px_rgba(212,160,23,0.2)]"
                    : "bg-[#0e1225] text-[#7a8899] border border-[#1a2040] hover:border-[#2a3060]"
              )}
            >
              {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
              {saving ? 'Saving...' : 'Save'}
            </button>

            <div className="h-5 w-px bg-[#1a2040]" />

            {/* Run / Cancel button */}
            {executing ? (
              <button
                onClick={handleCancel}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-[#ef4444]/20 text-[#ef4444] border border-[#ef4444]/30 hover:bg-[#ef4444]/30 transition-all"
              >
                <StopCircle className="w-3 h-3" />
                Cancel
              </button>
            ) : (
              <button
                onClick={handleRun}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-[#22c55e]/20 text-[#22c55e] border border-[#22c55e]/30 hover:bg-[#22c55e]/30 transition-all shadow-[0_0_10px_rgba(34,197,94,0.1)]"
              >
                <Play className="w-3 h-3" />
                Run
              </button>
            )}

            {/* History button */}
            <button
              onClick={() => { setShowHistory(!showHistory); if (!showHistory) fetchHistory(); }}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all border",
                showHistory
                  ? "bg-[#4a8cc7]/20 text-[#4a8cc7] border-[#4a8cc7]/30"
                  : "bg-[#0e1225] text-[#7a8899] border-[#1a2040] hover:border-[#2a3060]"
              )}
            >
              <History className="w-3 h-3" />
              History
            </button>
          </div>
        </div>

        {/* Execution Status Bar */}
        {runStatus && (
          <div className={cn(
            "flex items-center justify-between px-4 py-2 border-b text-[10px] font-bold uppercase tracking-wider",
            runStatus === 'running' ? "bg-[#4a8cc7]/10 border-[#4a8cc7]/20 text-[#4a8cc7]" :
            runStatus === 'completed' ? "bg-[#22c55e]/10 border-[#22c55e]/20 text-[#22c55e]" :
            runStatus === 'failed' ? "bg-[#ef4444]/10 border-[#ef4444]/20 text-[#ef4444]" :
            runStatus === 'cancelled' ? "bg-[#7a8899]/10 border-[#7a8899]/20 text-[#7a8899]" :
            "bg-[#d4a017]/10 border-[#d4a017]/20 text-[#d4a017]"
          )}>
            <div className="flex items-center gap-2">
              {runStatus === 'running' && <Loader2 className="w-3 h-3 animate-spin" />}
              {runStatus === 'completed' && <CheckCircle2 className="w-3 h-3" />}
              {runStatus === 'failed' && <XCircle className="w-3 h-3" />}
              {runStatus === 'pending' && <Clock className="w-3 h-3" />}
              <span>Flow {runStatus}</span>
            </div>
            <div className="flex items-center gap-2">
              {Object.values(nodeStates).length > 0 && (
                <span className="text-[9px] opacity-70">
                  {Object.values(nodeStates).filter((s: any) => s.status === 'completed').length}/{Object.values(nodeStates).length} nodes completed
                </span>
              )}
              {runStatus !== 'running' && (
                <button
                  onClick={() => { setRunStatus(null); setNodeStates({}); setNodes((nds) => nds.map((n) => ({ ...n, data: { ...n.data, execution_status: null } }))); }}
                  className="text-current opacity-50 hover:opacity-100 transition-opacity"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>
        )}

        {/* React Flow Canvas */}
        <div ref={reactFlowWrapper} className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            defaultViewport={flow.viewport}
            fitView={!flow.nodes?.length ? false : true}
            snapToGrid
            snapGrid={[16, 16]}
            deleteKeyCode={null}
            proOptions={{ hideAttribution: true }}
            style={{ background: '#060810' }}
          >
            <Controls
              position="bottom-left"
              style={{ display: 'flex', gap: 2 }}
              className="!bg-[#0e1225] !border !border-[#1a2040] !rounded-lg !shadow-lg [&>button]:!bg-[#0a0e1a] [&>button]:!border-[#1a2040] [&>button]:!text-[#7a8899] [&>button:hover]:!text-[#d4a017] [&>button]:!rounded [&>button]:!w-7 [&>button]:!h-7"
            />
            <MiniMap
              position="bottom-right"
              nodeColor={(n) => nodeColors[n.type || 'samurai'] || '#d4a017'}
              maskColor="rgba(6, 8, 16, 0.85)"
              className="!bg-[#0a0e1a] !border !border-[#1a2040] !rounded-lg"
              style={{ width: 160, height: 100 }}
            />
            <Background
              variant={BackgroundVariant.Dots}
              gap={20}
              size={1}
              color="#1a204040"
            />

            {/* Empty state */}
            {nodes.length === 0 && (
              <Panel position="top-center" className="mt-24">
                <div className="text-center space-y-3 animate-in fade-in duration-700">
                  <div className="w-16 h-16 rounded-2xl bg-[#0e1225] border border-[#1a2040] flex items-center justify-center mx-auto">
                    <GitBranch className="w-7 h-7 text-[#4a8cc7]/40" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-[#7a8899]">Empty Canvas</p>
                    <p className="text-[10px] text-[#7a8899]/60 mt-1">
                      Drag cards from the toolbar above to build your workflow
                    </p>
                  </div>
                </div>
              </Panel>
            )}
          </ReactFlow>
        </div>
      </div>

      {/* Inspector Panel */}
      {inspectorNode && (
        <NodeInspector
          node={inspectorNode}
          onUpdate={onNodeDataUpdate}
          onClose={() => setSelectedNode(null)}
          agents={agents}
          routingProfiles={routingProfiles}
        />
      )}

      {/* Run History Panel */}
      {showHistory && (
        <div className="w-[320px] bg-[#0a0e1a] border-l border-[#1a2040] flex flex-col shrink-0">
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#1a2040]">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-[#4a8cc7]" />
              <h3 className="text-xs font-bold text-[#c8d0d8] uppercase tracking-wider">Run History</h3>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={fetchHistory}
                className="p-1 hover:bg-[#1a2040] text-[#7a8899] hover:text-[#c8d0d8] rounded transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setShowHistory(false)}
                className="p-1 hover:bg-[#1a2040] text-[#7a8899] hover:text-[#c8d0d8] rounded transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {runHistory.length === 0 && (
              <div className="text-center py-8">
                <Clock className="w-8 h-8 text-[#7a8899]/30 mx-auto mb-2" />
                <p className="text-[10px] text-[#7a8899]/50">No runs yet</p>
              </div>
            )}
            {runHistory.map((run: any) => (
              <div
                key={run.id}
                className="p-3 bg-[#0e1225] border border-[#1a2040] rounded-lg hover:border-[#2a3060] transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    {run.status === 'completed' && <CheckCircle2 className="w-3.5 h-3.5 text-[#22c55e]" />}
                    {run.status === 'failed' && <XCircle className="w-3.5 h-3.5 text-[#ef4444]" />}
                    {run.status === 'running' && <Loader2 className="w-3.5 h-3.5 text-[#4a8cc7] animate-spin" />}
                    {run.status === 'cancelled' && <StopCircle className="w-3.5 h-3.5 text-[#7a8899]" />}
                    {run.status === 'pending' && <Clock className="w-3.5 h-3.5 text-[#d4a017]" />}
                    <span className={cn(
                      "text-[10px] font-bold uppercase",
                      run.status === 'completed' ? "text-[#22c55e]" :
                      run.status === 'failed' ? "text-[#ef4444]" :
                      run.status === 'running' ? "text-[#4a8cc7]" :
                      "text-[#7a8899]"
                    )}>
                      {run.status}
                    </span>
                  </div>
                  <span className="text-[8px] font-bold uppercase tracking-widest text-[#7a8899]/60 bg-[#7a8899]/10 px-1.5 py-0.5 rounded">
                    {run.trigger_type}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[9px] text-[#7a8899]">
                  <span>{run.created_at ? new Date(run.created_at).toLocaleString() : '-'}</span>
                  {run.started_at && run.completed_at && (
                    <span className="text-[#d4a017]/70">
                      {((new Date(run.completed_at).getTime() - new Date(run.started_at).getTime()) / 1000).toFixed(1)}s
                    </span>
                  )}
                </div>
                {run.error_message && (
                  <p className="mt-1.5 text-[9px] text-[#ef4444]/80 line-clamp-2 bg-[#ef4444]/5 rounded p-1.5">
                    {run.error_message}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════
// FLOW LIST VIEW
// ═══════════════════════════════════════════════════════════════

function FlowListView({
  flows,
  loading,
  onSelect,
  onCreate,
  onDelete,
  onDuplicate,
  onRefresh,
}: {
  flows: FlowListItem[];
  loading: boolean;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
  onDuplicate: (id: string) => void;
  onRefresh: () => void;
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [menuOpen, setMenuOpen] = useState<string | null>(null);

  const filtered = flows.filter((f) =>
    f.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const statusColors: Record<string, string> = {
    draft: '#7a8899',
    active: '#22c55e',
    paused: '#4a8cc7',
    archived: '#7a8899',
  };

  return (
    <div className="space-y-5 animate-in fade-in duration-500">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Flows', value: flows.length, color: '#d4a017' },
          { label: 'Active', value: flows.filter((f) => f.status === 'active').length, color: '#22c55e' },
          { label: 'Draft', value: flows.filter((f) => f.status === 'draft').length, color: '#7a8899' },
          { label: 'Paused', value: flows.filter((f) => f.status === 'paused').length, color: '#4a8cc7' },
        ].map((stat, i) => (
          <div key={i} className="shogun-card !p-4 border-l-2" style={{ borderLeftColor: stat.color }}>
            <span className="text-[9px] uppercase tracking-widest font-bold text-[#7a8899]">{stat.label}</span>
            <div className="text-2xl font-bold text-[#c8d0d8] mt-1">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7a8899]" />
          <input
            type="text"
            placeholder="Filter workflows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0e1225] border border-[#1a2040] rounded-lg pl-10 pr-4 py-2 text-sm text-[#c8d0d8] focus:border-[#4a8cc7] transition-colors outline-none"
          />
        </div>
        <button
          onClick={onRefresh}
          className="p-2.5 bg-[#0e1225] border border-[#1a2040] rounded-lg text-[#7a8899] hover:text-[#d4a017] transition-colors"
        >
          <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
        </button>
        <button
          onClick={onCreate}
          className="flex items-center gap-2 bg-[#4a8cc7] hover:bg-[#4a8cc7]/90 text-white font-bold py-2.5 px-5 rounded-lg transition-all shadow-[0_0_20px_rgba(74,140,199,0.15)] text-xs"
        >
          <Plus className="w-4 h-4" /> NEW FLOW
        </button>
      </div>

      {/* Flow Cards Grid */}
      {loading ? (
        <div className="flex flex-col items-center gap-3 py-16">
          <Loader2 className="w-6 h-6 text-[#d4a017] animate-spin" />
          <span className="text-[10px] text-[#7a8899] uppercase tracking-widest">Loading workflows...</span>
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16">
          <GitBranch className="w-10 h-10 text-[#1a2040] mx-auto mb-3" />
          <p className="text-sm text-[#7a8899]">
            {flows.length === 0 ? 'No Agent Flows created yet' : 'No flows match your search'}
          </p>
          {flows.length === 0 && (
            <p className="text-[10px] text-[#7a8899]/60 mt-1">
              Create your first workflow to orchestrate Samurai agents visually
            </p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((flow) => (
            <button
              key={flow.id}
              onClick={() => onSelect(flow.id)}
              className="shogun-card !p-0 text-left hover:border-[#4a8cc7]/40 transition-all group relative overflow-hidden"
            >
              {/* Top accent */}
              <div className="h-0.5" style={{ background: statusColors[flow.status] || '#7a8899' }} />

              <div className="p-5">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-[#c8d0d8] group-hover:text-[#d4a017] transition-colors truncate">
                      {flow.name}
                    </h4>
                    <p className="text-[10px] text-[#7a8899] mt-1 line-clamp-2">
                      {flow.description || 'No description'}
                    </p>
                  </div>
                  <div className="relative">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setMenuOpen(menuOpen === flow.id ? null : flow.id);
                      }}
                      className="p-1.5 hover:bg-[#1a2040] rounded-lg text-[#7a8899] hover:text-[#c8d0d8] transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <MoreVertical className="w-3.5 h-3.5" />
                    </button>
                    {menuOpen === flow.id && (
                      <div className="absolute right-0 top-8 z-10 w-36 bg-[#0e1225] border border-[#1a2040] rounded-lg shadow-xl overflow-hidden">
                        <button
                          onClick={(e) => { e.stopPropagation(); onDuplicate(flow.id); setMenuOpen(null); }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-[10px] font-bold text-[#7a8899] hover:bg-[#1a2040] hover:text-[#c8d0d8] transition-colors"
                        >
                          <Copy className="w-3 h-3" /> Duplicate
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); onDelete(flow.id); setMenuOpen(null); }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-[10px] font-bold text-red-400 hover:bg-red-500/10 transition-colors"
                        >
                          <Trash2 className="w-3 h-3" /> Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 mt-4">
                  <span
                    className="text-[8px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border"
                    style={{
                      color: statusColors[flow.status],
                      background: `${statusColors[flow.status]}10`,
                      borderColor: `${statusColors[flow.status]}30`,
                    }}
                  >
                    {flow.status}
                  </span>
                  <span className="text-[8px] text-[#7a8899] flex items-center gap-1">
                    <Clock className="w-2.5 h-2.5" />
                    {flow.trigger_type}
                  </span>
                  <span className="text-[8px] text-[#7a8899]/60 ml-auto">
                    {new Date(flow.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════
// CREATE FLOW MODAL
// ═══════════════════════════════════════════════════════════════

function CreateFlowModal({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (name: string, description: string, triggerType: string) => void;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [triggerType, setTriggerType] = useState('manual');

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-[#0a0e1a] border border-[#1a2040] rounded-xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-[#0e1225] border-b border-[#1a2040] p-6 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-[#d4a017] flex items-center gap-2">
              <GitBranch className="w-5 h-5" />
              Create Agent Flow
            </h3>
            <p className="text-[10px] text-[#7a8899] uppercase tracking-widest font-bold mt-1">
              New Workflow Definition
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[#d4a017]/10 text-[#7a8899] hover:text-[#d4a017] rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <div className="p-6 space-y-5">
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-[#7a8899] uppercase tracking-widest">Flow Name</label>
            <input
              type="text"
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-[#050508] border border-[#1a2040] rounded-lg p-2.5 text-sm text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none"
              placeholder="e.g., Research Pipeline, Weekly Report..."
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-[#7a8899] uppercase tracking-widest">Trigger Type</label>
            <select
              value={triggerType}
              onChange={(e) => setTriggerType(e.target.value)}
              className="w-full bg-[#050508] border border-[#1a2040] rounded-lg p-2.5 text-sm text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none cursor-pointer"
            >
              <option value="manual">Manual Execution</option>
              <option value="scheduled">Scheduled / Cron</option>
              <option value="event">Event-Based Trigger</option>
              <option value="api">API Trigger</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-[#7a8899] uppercase tracking-widest">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full bg-[#050508] border border-[#1a2040] rounded-lg p-3 text-xs text-[#c8d0d8] focus:border-[#d4a017] transition-colors outline-none resize-none"
              placeholder="Describe the purpose of this workflow..."
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 pt-0 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-[#0e1225] hover:bg-[#1a2040] text-[#7a8899] font-bold py-2.5 rounded-lg transition-all border border-[#1a2040] text-sm"
          >
            Cancel
          </button>
          <button
            onClick={() => onCreate(name, description, triggerType)}
            disabled={!name.trim()}
            className={cn(
              "flex-1 font-bold py-2.5 rounded-lg transition-all text-sm flex items-center justify-center gap-2",
              !name.trim()
                ? "bg-[#7a8899]/20 text-[#7a8899] cursor-not-allowed"
                : "bg-[#4a8cc7] hover:bg-[#4a8cc7]/90 text-white shadow-[0_0_20px_rgba(74,140,199,0.15)]"
            )}
          >
            <Plus className="w-3.5 h-3.5" />
            Create Flow
          </button>
        </div>
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════
// MAIN EXPORT — AGENT FLOW TAB COMPONENT
// ═══════════════════════════════════════════════════════════════

export const AgentFlow = () => {
  const [flows, setFlows] = useState<FlowListItem[]>([]);
  const [activeFlow, setActiveFlow] = useState<AgentFlowData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [agents, setAgents] = useState<any[]>([]);
  const [routingProfiles, setRoutingProfiles] = useState<any[]>([]);

  // Fetch flows list
  const fetchFlows = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/v1/agent-flows');
      if (res.data.data) setFlows(res.data.data);
    } catch (err) {
      console.error('Failed to fetch flows:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch supporting data
  const fetchSupportData = useCallback(async () => {
    try {
      const [agentRes, routingRes] = await Promise.all([
        axios.get('/api/v1/agents?agent_type=samurai'),
        axios.get('/api/v1/model-routing-profiles'),
      ]);
      if (agentRes.data.data) setAgents(agentRes.data.data);
      if (routingRes.data.data) setRoutingProfiles(routingRes.data.data);
    } catch (err) {
      console.error('Failed to fetch support data:', err);
    }
  }, []);

  useEffect(() => {
    fetchFlows();
    fetchSupportData();
  }, [fetchFlows, fetchSupportData]);

  // Load a specific flow
  const loadFlow = useCallback(async (flowId: string) => {
    try {
      const res = await axios.get(`/api/v1/agent-flows/${flowId}`);
      if (res.data.data) setActiveFlow(res.data.data);
    } catch (err) {
      console.error('Failed to load flow:', err);
    }
  }, []);

  // Create new flow
  const handleCreate = useCallback(async (name: string, description: string, triggerType: string) => {
    try {
      const res = await axios.post('/api/v1/agent-flows', { name, description, trigger_type: triggerType });
      if (res.data.data) {
        setShowCreateModal(false);
        setActiveFlow(res.data.data);
        fetchFlows();
      }
    } catch (err) {
      console.error('Failed to create flow:', err);
    }
  }, [fetchFlows]);

  // Delete flow
  const handleDelete = useCallback(async (flowId: string) => {
    if (!confirm('Delete this Agent Flow?')) return;
    try {
      await axios.delete(`/api/v1/agent-flows/${flowId}`);
      fetchFlows();
    } catch (err) {
      console.error('Failed to delete flow:', err);
    }
  }, [fetchFlows]);

  // Duplicate flow
  const handleDuplicate = useCallback(async (flowId: string) => {
    try {
      await axios.post(`/api/v1/agent-flows/${flowId}/duplicate`);
      fetchFlows();
    } catch (err) {
      console.error('Failed to duplicate flow:', err);
    }
  }, [fetchFlows]);

  // Canvas view
  if (activeFlow) {
    return (
      <ReactFlowProvider>
        <AgentFlowCanvas
          key={activeFlow.id}
          flow={activeFlow}
          onBack={() => { setActiveFlow(null); fetchFlows(); }}
          onFlowUpdate={fetchFlows}
          agents={agents}
          routingProfiles={routingProfiles}
        />
      </ReactFlowProvider>
    );
  }

  // List view
  return (
    <>
      <FlowListView
        flows={flows}
        loading={loading}
        onSelect={loadFlow}
        onCreate={() => setShowCreateModal(true)}
        onDelete={handleDelete}
        onDuplicate={handleDuplicate}
        onRefresh={fetchFlows}
      />

      {showCreateModal && (
        <CreateFlowModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreate}
        />
      )}
    </>
  );
};

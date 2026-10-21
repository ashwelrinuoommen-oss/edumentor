import React, { useMemo, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  MarkerType,
  Handle,
  Position,
  useReactFlow,
  ReactFlowProvider,
  type Node,
  type Edge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Concept } from '../../services/mockService';
import { Badge } from '../ui/Badge';
import { Maximize2, Layers, Info } from 'lucide-react';
import { cn } from '../../utils/cn';

interface ConceptFlowGraphProps {
  concepts: Concept[];
  activeConceptId?: string;
  onSelectConcept?: (conceptId: string) => void;
  className?: string;
  height?: string;
}

// Custom Node for Concept Flow: Left-to-Right layout with status colors & hover tooltip
function ConceptNodeComponent({ data }: { data: any }) {
  const [isHovered, setIsHovered] = useState(false);

  const isMastered = data.status === 'mastered';
  const isWeak = data.status === 'weak' || data.status === 'review_due';
  const isInProgress = data.status === 'in_progress';
  const isUnstudied = data.status === 'unstudied' || !data.status;
  const isActive = data.isActive;

  // Status-based styling
  const getBorderColor = () => {
    if (isActive) return 'border-[#2DD4BF] ring-2 ring-[#2DD4BF]/50 shadow-lg shadow-[#2DD4BF]/10';
    if (isMastered) return 'border-[#34D399]/70 ring-1 ring-[#34D399]/30';
    if (isWeak) return 'border-[#F87171]/70 ring-1 ring-[#F87171]/30';
    if (isInProgress) return 'border-[#2DD4BF]/70 ring-1 ring-[#2DD4BF]/30';
    return 'border-[#262626] hover:border-[#383838]';
  };

  const getStatusText = () => {
    if (isMastered) return 'Mastered';
    if (isWeak) return 'Weak';
    if (isInProgress) return 'In Progress';
    return 'Unstudied';
  };

  const getStatusBadgeVariant = () => {
    if (isMastered) return 'success';
    if (isWeak) return 'weak';
    if (isInProgress) return 'teal';
    return 'neutral';
  };

  return (
    <div 
      className="relative select-none"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Target handle on Left (incoming from prerequisite) */}
      <Handle 
        type="target" 
        position={Position.Left} 
        className="!bg-[#2DD4BF] !w-2.5 !h-2.5 !border-2 !border-[#0A0A0A]" 
      />

      {/* Main Node Card */}
      <div
        onClick={() => data.onSelect?.(data.id)}
        className={cn(
          'w-64 p-3.5 rounded-[12px] bg-[#171717] transition-all duration-150 cursor-pointer text-left shadow-md',
          getBorderColor(),
          'hover:bg-[#1F1F1F]'
        )}
        id={`graph-node-${data.id}`}
        title="Click to view details and edit concept"
      >
        {/* Header: Order badge & Difficulty */}
        <div className="flex items-center justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-1.5">
            <span className="w-5 h-5 rounded-full bg-[#111111] border border-[#262626] text-[10px] font-bold text-[#EDEDED] flex items-center justify-center shrink-0">
              #{data.orderIndex}
            </span>
            <Badge
              variant={getStatusBadgeVariant()}
              className="text-[10px] py-0 px-2 uppercase tracking-wider font-semibold"
            >
              {getStatusText()}
            </Badge>
          </div>

          <Badge
            variant={
              data.difficulty === 'Beginner' 
                ? 'success' 
                : data.difficulty === 'Intermediate' 
                  ? 'caution' 
                  : 'teal'
            }
            className="text-[9px] py-0 px-1.5"
          >
            {data.difficulty}
          </Badge>
        </div>

        {/* Title */}
        <div className="text-xs font-semibold text-[#EDEDED] truncate mb-1" title={data.title}>
          {data.title}
        </div>

        {/* Clamped Definition from Notes */}
        <p className="text-[11px] text-[#A3A3A3] line-clamp-2 leading-relaxed mb-2.5">
          {data.summary || data.rawContent}
        </p>

        {/* Footer: Prerequisites count */}
        <div className="flex items-center justify-between pt-1.5 border-t border-[#262626] text-[10px] text-[#737373]">
          <span>
            {(data.prerequisiteIds || []).length > 0 
              ? `${(data.prerequisiteIds || []).length} prerequisite${(data.prerequisiteIds || []).length > 1 ? 's' : ''}`
              : 'Foundation concept'}
          </span>
          <span className="text-[#2DD4BF] hover:underline">View details →</span>
        </div>
      </div>

      {/* Source handle on Right (outgoing to dependent concept) */}
      <Handle 
        type="source" 
        position={Position.Right} 
        className="!bg-[#2DD4BF] !w-2.5 !h-2.5 !border-2 !border-[#0A0A0A]" 
      />

      {/* Hover Tooltip showing full definition from notes */}
      {isHovered && (
        <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-72 p-3 bg-[#111111] border border-[#262626] rounded-[10px] shadow-2xl z-50 pointer-events-none text-xs text-[#EDEDED] animate-fade-in">
          <div className="flex items-center gap-1.5 text-[10px] font-semibold text-[#2DD4BF] uppercase tracking-wider mb-1">
            <Info size={11} />
            <span>Definition from notes</span>
          </div>
          <p className="text-[11px] text-[#A3A3A3] leading-relaxed">
            {data.summary || data.rawContent}
          </p>
        </div>
      )}
    </div>
  );
}

const nodeTypes = {
  conceptNode: ConceptNodeComponent
};

// Inner Graph component that can use React Flow hooks
function ConceptFlowGraphInner({ 
  concepts = [], 
  activeConceptId,
  onSelectConcept,
  className,
  height = '420px'
}: ConceptFlowGraphProps) {
  const { fitView } = useReactFlow();

  // Generate nodes in LEFT TO RIGHT layers based on prerequisite depth
  const { nodes, edges } = useMemo(() => {
    if (!concepts || concepts.length === 0) {
      return { nodes: [], edges: [] };
    }

    const flowNodes: Node[] = [];
    const flowEdges: Edge[] = [];

    // Calculate layer / depth for each concept (distance from foundation nodes)
    const layerMap = new Map<string, number>();
    concepts.forEach(c => layerMap.set(c.id, 0));

    // Multi-pass layer calculation
    for (let pass = 0; pass < concepts.length; pass++) {
      let changed = false;
      concepts.forEach(c => {
        const currentLvl = layerMap.get(c.id) || 0;
        (c.prerequisiteIds || []).forEach(pId => {
          if (layerMap.has(pId)) {
            const pLvl = layerMap.get(pId) || 0;
            if (pLvl + 1 > currentLvl) {
              layerMap.set(c.id, pLvl + 1);
              changed = true;
            }
          }
        });
      });
      if (!changed) break;
    }

    // Group concepts by layer (Layer 0, Layer 1, Layer 2...)
    const layerGroups = new Map<number, Concept[]>();
    concepts.forEach(c => {
      const lvl = layerMap.get(c.id) || 0;
      if (!layerGroups.has(lvl)) layerGroups.set(lvl, []);
      layerGroups.get(lvl)!.push(c);
    });

    // Layout configuration for LEFT TO RIGHT flow
    const NODE_WIDTH = 270;
    const NODE_HEIGHT = 150;
    const LAYER_GAP_X = 140; // Horizontal gap between layers
    const NODE_GAP_Y = 50;   // Vertical gap between nodes in same layer

    // Find maximum nodes in any layer to vertically balance columns
    let maxNodesInLayer = 1;
    layerGroups.forEach(grp => {
      if (grp.length > maxNodesInLayer) maxNodesInLayer = grp.length;
    });
    const totalMaxHeight = maxNodesInLayer * (NODE_HEIGHT + NODE_GAP_Y);

    layerGroups.forEach((group, layerIdx) => {
      const x = 50 + layerIdx * (NODE_WIDTH + LAYER_GAP_X);
      const groupHeight = group.length * (NODE_HEIGHT + NODE_GAP_Y) - NODE_GAP_Y;
      const startY = Math.max(40, (totalMaxHeight - groupHeight) / 2);

      group.forEach((concept, rowIdx) => {
        const y = startY + rowIdx * (NODE_HEIGHT + NODE_GAP_Y);

        flowNodes.push({
          id: concept.id,
          type: 'conceptNode',
          position: { x, y },
          data: {
            ...concept,
            isActive: concept.id === activeConceptId,
            onSelect: onSelectConcept
          }
        });

        // Add directed edges from each prerequisite to this concept (left -> right)
        (concept.prerequisiteIds || []).forEach(prereqId => {
          flowEdges.push({
            id: `edge-${prereqId}-${concept.id}`,
            source: prereqId,
            target: concept.id,
            type: 'smoothstep',
            animated: true,
            style: { 
              stroke: '#2DD4BF', 
              strokeWidth: 2,
              opacity: 0.85
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#2DD4BF',
              width: 16,
              height: 16
            }
          });
        });
      });
    });

    return { nodes: flowNodes, edges: flowEdges };
  }, [concepts, activeConceptId, onSelectConcept]);

  return (
    <div 
      className={cn(
        "w-full bg-[#0E0E0E] rounded-[12px] border border-[#262626] overflow-hidden relative",
        className
      )}
      style={{ height }}
    >
      {/* Top Banner & Fit to Screen Button */}
      <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between pointer-events-none">
        <div className="px-2.5 py-1 bg-[#171717]/90 backdrop-blur-sm border border-[#262626] rounded-md text-[11px] text-[#A3A3A3] flex items-center gap-1.5 pointer-events-auto">
          <Layers size={13} className="text-[#2DD4BF]" />
          <span>Prerequisite Graph (Left → Right Learning Flow)</span>
        </div>

        <button
          type="button"
          onClick={() => fitView({ padding: 0.2, duration: 400 })}
          className="px-2.5 py-1 bg-[#171717]/90 hover:bg-[#1F1F1F] text-[#EDEDED] backdrop-blur-sm border border-[#262626] rounded-md text-[11px] flex items-center gap-1.5 transition-colors pointer-events-auto shadow-md"
          title="Fit diagram to screen"
          id="btn-fit-to-screen"
        >
          <Maximize2 size={12} />
          <span>Fit to screen</span>
        </button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        minZoom={0.3}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
        className="bg-[#0A0A0A]"
      >
        <Background color="#262626" gap={20} size={1} />
        <Controls 
          showInteractive={false} 
          className="!bg-[#171717] !border-[#262626] !rounded-md !text-[#EDEDED]" 
        />
        {/* Dark-themed MiniMap */}
        <MiniMap
          nodeColor={(n) => {
            const status = (n.data as any)?.status;
            if (status === 'mastered') return '#34D399';
            if (status === 'weak' || status === 'review_due') return '#F87171';
            if (status === 'in_progress') return '#2DD4BF';
            return '#525252';
          }}
          maskColor="rgba(10, 10, 10, 0.75)"
          className="!bg-[#111111] !border-[#262626] !rounded-[8px] !overflow-hidden"
          zoomable
          pannable
        />
      </ReactFlow>
    </div>
  );
}

export function ConceptFlowGraph(props: ConceptFlowGraphProps) {
  return (
    <ReactFlowProvider>
      <ConceptFlowGraphInner {...props} />
    </ReactFlowProvider>
  );
}

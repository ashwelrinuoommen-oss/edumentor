import React from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Cell 
} from 'recharts';

export interface WeakestConceptItem {
  id: string;
  title: string;
  moduleName: string;
  lastScore: number; // 0 - 5.0
  color: string;
}

interface WeakestConceptsBarChartProps {
  data: WeakestConceptItem[];
}

export function WeakestConceptsBarChart({ data }: WeakestConceptsBarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-72 bg-[#111111] p-6 rounded-[16px] border border-[#262626] flex flex-col items-center justify-center text-center gap-2">
        <span className="text-xs text-[#737373]">No recall evaluations recorded yet.</span>
        <span className="text-[11px] text-[#A3A3A3]">As you answer concept questions, weak topics will appear here.</span>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload as WeakestConceptItem;
      return (
        <div className="p-3 rounded-[10px] bg-[#171717] border border-[#262626] shadow-xl text-xs flex flex-col gap-1 max-w-xs">
          <span className="font-semibold text-[#EDEDED] text-xs leading-snug">
            {item.title}
          </span>
          <span className="text-[11px] text-[#737373] truncate">
            Module: {item.moduleName}
          </span>
          <div className="flex items-center gap-2 mt-0.5 pt-1 border-t border-[#262626]">
            <span 
              className="text-xs font-bold font-mono px-1.5 py-0.5 rounded border"
              style={{ backgroundColor: `${item.color}20`, color: item.color, borderColor: `${item.color}40` }}
            >
              {item.lastScore.toFixed(1)} / 5.0
            </span>
            <span className="text-[10px] text-[#A3A3A3]">
              {item.lastScore < 2.5 ? 'Needs Work' : item.lastScore < 4.0 ? 'Partial' : 'Strong'}
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-72 bg-[#111111] p-4 sm:p-5 rounded-[16px] border border-[#262626] flex flex-col gap-3" id="chart-weakest-concepts">
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <h3 className="text-xs font-semibold text-[#EDEDED]">Weakest Concepts</h3>
          <span className="text-[11px] text-[#737373]">Prioritized topics that benefit most from review</span>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-[#737373]">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#F87171]" />
            <span>&lt; 2.5</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#FBBF24]" />
            <span>2.5–3.9</span>
          </span>
        </div>
      </div>

      <div className="w-full flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 15, left: -20, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" vertical={false} />
            <XAxis 
              dataKey="title" 
              stroke="#737373" 
              fontSize={10} 
              tickLine={false}
              axisLine={{ stroke: '#262626' }}
              interval={0}
              angle={-20}
              textAnchor="end"
              tickFormatter={(val: string) => val.length > 13 ? `${val.slice(0, 12)}…` : val}
            />
            <YAxis 
              stroke="#737373" 
              fontSize={11} 
              tickLine={false} 
              axisLine={{ stroke: '#262626' }}
              domain={[0, 5]} 
              ticks={[0, 1, 2, 3, 4, 5]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="lastScore" radius={[6, 6, 0, 0]} maxBarSize={48}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

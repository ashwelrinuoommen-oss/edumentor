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

interface RetentionBarChartProps {
  data?: Array<{ stage: string; count: number; color: string }>;
}

const DEFAULT_STAGES = [
  { stage: 'Due Today', count: 3, color: '#F87171' },
  { stage: '1-3 Days', count: 5, color: '#FBBF24' },
  { stage: '4-7 Days', count: 8, color: '#2DD4BF' },
  { stage: '14+ Days', count: 12, color: '#34D399' }
];

export function RetentionBarChart({ data = DEFAULT_STAGES }: RetentionBarChartProps) {
  return (
    <div className="w-full h-64 bg-[#111111] p-4 rounded-[12px] border border-[#262626]">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-semibold text-[#EDEDED]">SM-2 Interval Distribution</h4>
        <span className="text-[11px] text-[#A3A3A3]">Total: {data.reduce((a, b) => a + b.count, 0)} concepts</span>
      </div>

      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
          <XAxis 
            dataKey="stage" 
            stroke="#737373" 
            fontSize={11} 
            tickLine={false} 
          />
          <YAxis 
            stroke="#737373" 
            fontSize={11} 
            tickLine={false} 
            allowDecimals={false} 
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#171717', 
              borderColor: '#262626', 
              borderRadius: '8px', 
              color: '#EDEDED',
              fontSize: '12px' 
            }} 
          />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

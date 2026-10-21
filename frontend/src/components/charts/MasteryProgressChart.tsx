import React from 'react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

interface MasteryProgressChartProps {
  data?: Array<{ name: string; score: number; retention: number }>;
}

const DEFAULT_DATA = [
  { name: 'Day 1', score: 45, retention: 50 },
  { name: 'Day 2', score: 62, retention: 65 },
  { name: 'Day 3', score: 78, retention: 75 },
  { name: 'Day 4', score: 74, retention: 80 },
  { name: 'Day 5', score: 86, retention: 88 },
  { name: 'Day 6', score: 91, retention: 93 },
  { name: 'Day 7', score: 94, retention: 96 }
];

export function MasteryProgressChart({ data = DEFAULT_DATA }: MasteryProgressChartProps) {
  return (
    <div className="w-full h-64 bg-[#111111] p-4 rounded-[12px] border border-[#262626]">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-semibold text-[#EDEDED]">Recall Retention & Score Trajectory</h4>
        <div className="flex items-center gap-4 text-[11px] text-[#A3A3A3]">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#2DD4BF]" />
            <span>Hybrid Score</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#34D399]" />
            <span>Retention Probability</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2DD4BF" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#2DD4BF" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="retGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#34D399" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#34D399" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
          <XAxis 
            dataKey="name" 
            stroke="#737373" 
            fontSize={11} 
            tickLine={false} 
          />
          <YAxis 
            stroke="#737373" 
            fontSize={11} 
            tickLine={false} 
            domain={[0, 100]} 
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
          <Area 
            type="monotone" 
            dataKey="score" 
            stroke="#2DD4BF" 
            strokeWidth={2} 
            fillOpacity={1} 
            fill="url(#scoreGrad)" 
          />
          <Area 
            type="monotone" 
            dataKey="retention" 
            stroke="#34D399" 
            strokeWidth={1.5} 
            strokeDasharray="4 4"
            fillOpacity={1} 
            fill="url(#retGrad)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

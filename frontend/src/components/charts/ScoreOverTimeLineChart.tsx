import React from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

export interface ScoreTrendPoint {
  date: string;
  averageScore: number; // 0 - 5.0
  sessionName?: string;
  conceptCount: number;
}

interface ScoreOverTimeLineChartProps {
  data: ScoreTrendPoint[];
}

export function ScoreOverTimeLineChart({ data }: ScoreOverTimeLineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="w-full h-64 bg-[#111111] p-6 rounded-[14px] border border-[#262626] flex flex-col items-center justify-center text-center gap-2">
        <span className="text-xs text-[#737373]">No recall sessions recorded yet.</span>
        <span className="text-[11px] text-[#A3A3A3]">Complete a recall session to plot your score trajectory.</span>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload as ScoreTrendPoint;
      return (
        <div className="p-3 rounded-[10px] bg-[#171717] border border-[#262626] shadow-xl text-xs flex flex-col gap-1">
          <span className="text-[11px] font-mono text-[#737373]">{label}</span>
          <div className="flex items-center gap-2">
            <span className="text-base font-bold font-mono text-[#2DD4BF]">
              {item.averageScore.toFixed(1)} / 5.0
            </span>
            <span className="text-[10px] text-[#A3A3A3]">avg score</span>
          </div>
          {item.sessionName && (
            <span className="text-[11px] text-[#EDEDED] font-medium truncate max-w-[180px]">
              {item.sessionName}
            </span>
          )}
          <span className="text-[10px] text-[#737373]">
            {item.conceptCount} concept{item.conceptCount === 1 ? '' : 's'} recalled
          </span>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-72 bg-[#111111] p-4 sm:p-5 rounded-[16px] border border-[#262626] flex flex-col gap-3" id="chart-score-over-time">
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <h3 className="text-xs font-semibold text-[#EDEDED]">Average Score Over Time</h3>
          <span className="text-[11px] text-[#737373]">Historical recall performance on 0–5 scale</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-[#2DD4BF] font-mono font-medium">
          <span className="w-2 h-2 rounded-full bg-[#2DD4BF]" />
          <span>Average Score</span>
        </div>
      </div>

      <div className="w-full flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 15, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F1F1F" vertical={false} />
            <XAxis 
              dataKey="date" 
              stroke="#737373" 
              fontSize={11} 
              tickLine={false}
              axisLine={{ stroke: '#262626' }}
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
            <Line 
              type="monotone" 
              dataKey="averageScore" 
              stroke="#2DD4BF" 
              strokeWidth={2.5}
              dot={{ fill: '#0A0A0A', stroke: '#2DD4BF', strokeWidth: 2, r: 4 }}
              activeDot={{ fill: '#2DD4BF', stroke: '#EDEDED', strokeWidth: 2, r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

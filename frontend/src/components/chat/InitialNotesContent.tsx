import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface InitialNotesContentProps {
  content: string;
  isInitial?: boolean;
}

export function InitialNotesContent({ content, isInitial }: InitialNotesContentProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const isLong = content.length > 280;

  if (!isLong || !isInitial) {
    return (
      <div className="whitespace-pre-wrap leading-relaxed text-[#EDEDED] text-sm">
        {content}
      </div>
    );
  }

  const truncated = content.slice(0, 280) + '...';

  return (
    <div className="flex flex-col gap-2">
      <div className="whitespace-pre-wrap leading-relaxed text-[#EDEDED] text-sm">
        {isExpanded ? content : truncated}
      </div>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-xs font-medium text-[#2DD4BF] hover:text-[#5eead4] self-start inline-flex items-center gap-1 focus-visible:ring-1 focus-visible:ring-[#2DD4BF] rounded px-1 -ml-1 transition-colors"
      >
        <span>{isExpanded ? 'Show less' : 'Show more'}</span>
        {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>
    </div>
  );
}

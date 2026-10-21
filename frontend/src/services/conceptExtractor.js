/**
 * Concept Extraction & Prerequisite Ordering Engine
 * Parses raw notes/markdown, extracts key concepts, extracts keywords/prerequisites,
 * and performs topological sorting to build a structured study path.
 */

// Common stop words to exclude when inferring keywords
const STOP_WORDS = new Set([
  'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t',
  'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
  'can', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing',
  'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t',
  'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers',
  'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in',
  'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t',
  'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our',
  'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s',
  'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs',
  'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re',
  'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t',
  'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s',
  'where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t',
  'would', 'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself',
  'yourselves', 'concept', 'notes', 'chapter', 'section', 'definition', 'overview', 'summary', 'details'
]);

/**
 * Extracts distinct concepts from raw text/markdown.
 */
export function extractConceptsFromText(rawText, deckTitle = 'Study Session') {
  if (!rawText || !rawText.trim()) return [];

  const lines = rawText.split('\n');
  const sections = [];
  let currentSection = null;

  // Pattern matching for headers or numbered topics:
  // e.g. "## 1. Virtual Address Space", "### Virtual Memory", "1. Concept Name", "**1. Paging**"
  const headerRegex = /^(?:#{1,4}\s+|\d+\.\s+|\*\*\s*(?:\d+\.\s*)?)(.+?)(?:\s*\*\*)?$/;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Check if line represents a new concept header
    const isMarkdownHeader = line.startsWith('#') && !line.startsWith('#####');
    const isNumberedHeader = /^\d+[\.\)]\s+[A-Z]/.test(line);
    const isBoldHeader = /^\*\*[A-Z].+\*\*$/.test(line);

    // Skip the main document title (single #) if it matches the deck overview
    if (line.startsWith('# ') && sections.length === 0 && !currentSection) {
      continue;
    }

    if (isMarkdownHeader || isNumberedHeader || isBoldHeader) {
      if (currentSection && currentSection.bodyLines.length > 0) {
        sections.push(currentSection);
      }

      let title = line.replace(/^[#\*\d\.\)\s]+/, '').replace(/\*\*$/, '').trim();
      currentSection = {
        title,
        bodyLines: []
      };
    } else {
      if (currentSection) {
        currentSection.bodyLines.push(line);
      } else {
        // If we haven't hit a header yet, create a prelude/first concept
        currentSection = {
          title: 'Core Fundamentals',
          bodyLines: [line]
        };
      }
    }
  }

  if (currentSection && currentSection.bodyLines.length > 0) {
    sections.push(currentSection);
  }

  // If no sections were extracted (e.g., pure uninterrupted paragraphs), fallback to paragraph segmentation
  if (sections.length === 0) {
    return parseFallbackParagraphs(rawText);
  }

  // Parse structured concepts from sections
  const extractedList = sections.map((sec, index) => {
    const bodyText = sec.bodyLines.join('\n');
    const summary = extractSummary(sec.bodyLines);
    const keyTerms = extractKeyTerms(sec.bodyLines, sec.title);
    const prerequisites = extractPrerequisites(sec.bodyLines);

    return {
      id: `concept-${Date.now()}-${index + 1}`,
      title: cleanTitle(sec.title),
      summary,
      rawContent: bodyText,
      keyTerms,
      prerequisites, // raw title strings
      prerequisiteIds: [],
      difficulty: 'Beginner', // will be adjusted after sorting
      estTimeMinutes: Math.max(2, Math.min(6, Math.round(keyTerms.length * 0.8 + 2))),
      orderIndex: index + 1,
      status: 'unstudied',
      sm2: {
        repetition: 0,
        interval: 0,
        easinessFactor: 2.5,
        nextReviewDate: null,
        lastScore: null,
        history: []
      }
    };
  });

  // Re-order based on prerequisites (Topological sorting)
  const orderedConcepts = orderConceptsByPrerequisites(extractedList);
  return orderedConcepts;
}

/**
 * Cleans section headers of numbers or excess symbols
 */
function cleanTitle(title) {
  return title
    .replace(/^\d+[\.\)]\s*/, '')
    .replace(/^Chapter\s+\d+:\s*/i, '')
    .replace(/^Section\s+\d+:\s*/i, '')
    .trim();
}

/**
 * Extracts a concise summary from the leading sentences of a section
 */
function extractSummary(lines) {
  const contentLines = lines.filter(l => 
    !l.toLowerCase().startsWith('keywords:') &&
    !l.toLowerCase().startsWith('- keywords:') &&
    !l.toLowerCase().startsWith('prerequisites:') &&
    !l.toLowerCase().startsWith('- prerequisites:')
  );

  for (const line of contentLines) {
    const clean = line.replace(/^[-*•]\s*/, '').trim();
    if (clean.length > 25) {
      return clean;
    }
  }

  return contentLines.join(' ').slice(0, 160) + '...';
}

/**
 * Extracts explicitly defined or inferred key terms
 */
function extractKeyTerms(lines, title) {
  const terms = new Set();

  // 1. Look for explicit "Keywords: ..." or "Key terms: ..." lines
  for (const line of lines) {
    const match = line.match(/(?:keywords|key terms|vocabulary):\s*(.+)$/i);
    if (match) {
      const items = match[1].split(/[,;]/);
      for (const item of items) {
        const cleaned = item.trim().replace(/^[-*•]\s*/, '').replace(/\.$/, '');
        if (cleaned.length > 1) {
          terms.add(cleaned);
        }
      }
    }
  }

  // 2. Extract bolded terms in markdown e.g. **Page Tables** or `terms`
  for (const line of lines) {
    const boldMatches = line.matchAll(/\*\*(.+?)\*\*/g);
    for (const m of boldMatches) {
      const candidate = m[1].trim();
      if (candidate.length > 2 && candidate.length < 35 && !candidate.toLowerCase().includes('prerequisite')) {
        terms.add(candidate);
      }
    }
    const codeMatches = line.matchAll(/`([^`]+)`/g);
    for (const m of codeMatches) {
      const candidate = m[1].trim();
      if (candidate.length > 2 && candidate.length < 25) {
        terms.add(candidate);
      }
    }
  }

  // 3. If few terms, extract salient noun phrases from title
  if (terms.size < 3) {
    const titleWords = title.split(/\s+/).filter(w => !STOP_WORDS.has(w.toLowerCase()));
    if (titleWords.length > 0) {
      terms.add(titleWords.join(' '));
    }
  }

  return Array.from(terms).slice(0, 8);
}

/**
 * Extracts explicitly listed prerequisites from note lines
 */
function extractPrerequisites(lines) {
  const prereqs = [];
  for (const line of lines) {
    const match = line.match(/(?:prerequisites|prerequisite|requires|builds on|builds upon):\s*(.+)$/i);
    if (match) {
      const items = match[1].split(/[,;]/);
      for (const item of items) {
        const clean = item.trim().replace(/^[-*•]\s*/, '').replace(/\.$/, '');
        if (clean.length > 1) {
          prereqs.push(clean);
        }
      }
    }
  }
  return prereqs;
}

/**
 * Orders concepts by prerequisite graph (Topological DAG Sort)
 */
export function orderConceptsByPrerequisites(concepts) {
  if (concepts.length <= 1) return concepts;

  // Build lookup by lower-case title for flexible matching
  const titleToConcept = new Map();
  concepts.forEach(c => {
    titleToConcept.set(c.title.toLowerCase(), c);
  });

  // Build adjacency graph: prereq -> dependent
  const inDegree = new Map();
  const graph = new Map();

  concepts.forEach(c => {
    inDegree.set(c.id, 0);
    graph.set(c.id, []);
  });

  // Resolve dependencies
  concepts.forEach(concept => {
    const matchedPrereqIds = [];

    concept.prerequisites.forEach(prereqStr => {
      const pLower = prereqStr.toLowerCase();
      // Look for exact match or substring match among existing concepts
      let found = null;
      for (const [key, cand] of titleToConcept.entries()) {
        if (key === pLower || key.includes(pLower) || pLower.includes(key)) {
          if (cand.id !== concept.id) {
            found = cand;
            break;
          }
        }
      }

      if (found && !matchedPrereqIds.includes(found.id)) {
        matchedPrereqIds.push(found.id);
        graph.get(found.id).push(concept.id);
        inDegree.set(concept.id, inDegree.get(concept.id) + 1);
      }
    });

    concept.prerequisiteIds = matchedPrereqIds;
  });

  // Kahn's Algorithm
  const queue = [];
  concepts.forEach(c => {
    if (inDegree.get(c.id) === 0) {
      queue.push(c);
    }
  });

  const sorted = [];
  while (queue.length > 0) {
    const current = queue.shift();
    sorted.push(current);

    const dependents = graph.get(current.id) || [];
    for (const depId of dependents) {
      inDegree.set(depId, inDegree.get(depId) - 1);
      if (inDegree.get(depId) === 0) {
        const depConcept = concepts.find(c => c.id === depId);
        if (depConcept) queue.push(depConcept);
      }
    }
  }

  // Handle cycles or disconnected nodes
  if (sorted.length < concepts.length) {
    const includedIds = new Set(sorted.map(s => s.id));
    concepts.forEach(c => {
      if (!includedIds.has(c.id)) {
        sorted.push(c);
      }
    });
  }

  // Assign order indices and computed difficulty based on depth
  return sorted.map((concept, idx) => {
    const prereqCount = concept.prerequisiteIds.length;
    let difficulty = 'Beginner';
    if (prereqCount >= 2 || idx >= Math.floor(sorted.length * 0.65)) {
      difficulty = 'Advanced';
    } else if (prereqCount === 1 || idx >= Math.floor(sorted.length * 0.35)) {
      difficulty = 'Intermediate';
    }

    return {
      ...concept,
      orderIndex: idx + 1,
      difficulty
    };
  });
}

/**
 * Fallback parser for unstructured text without clear headers
 */
function parseFallbackParagraphs(rawText) {
  const paragraphs = rawText
    .split(/\n\s*\n/)
    .map(p => p.trim())
    .filter(p => p.length > 30);

  if (paragraphs.length === 0) {
    paragraphs.push(rawText.trim());
  }

  return paragraphs.slice(0, 8).map((para, idx) => {
    const firstSentence = (para.match(/^[^.!?]+[.!?]/) || [para.slice(0, 60)])[0].trim();
    const words = firstSentence.split(/\s+/).slice(0, 5).join(' ');

    return {
      id: `concept-${Date.now()}-${idx + 1}`,
      title: `Concept ${idx + 1}: ${words}`,
      summary: firstSentence,
      rawContent: para,
      keyTerms: ['Core Principle', 'Recall Target'],
      prerequisites: idx > 0 ? [`Concept ${idx}`] : [],
      prerequisiteIds: [],
      difficulty: idx === 0 ? 'Beginner' : idx > 2 ? 'Advanced' : 'Intermediate',
      estTimeMinutes: 3,
      orderIndex: idx + 1,
      status: 'unstudied',
      sm2: {
        repetition: 0,
        interval: 0,
        easinessFactor: 2.5,
        nextReviewDate: null,
        lastScore: null,
        history: []
      }
    };
  });
}

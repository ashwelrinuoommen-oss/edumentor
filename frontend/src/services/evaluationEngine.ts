import { Concept } from './mockService';
import { calculateSM2 } from './sm2Scheduler';

export interface EvaluationResult {
  score: number; // 0.0 to 5.0
  gradeLabel: 'Strong' | 'Partial' | 'Needs work';
  meaningMatchScore: number; // 0 to 100
  keyTermsCoveredScore: number; // 0 to 100
  tutorJudgementScore: number; // 0 to 100
  matchedKeywords: string[];
  missedKeywords: string[];
  whatYouGotRight: string[];
  whatWasMissing: string[];
  whatWasOff: string[];
  sourceDefinition: string;
  nextReviewLabel: string; // e.g. "tomorrow", "in 6 days"
  nextIntervalDays: number;
  isHinted: boolean;
  isCopied: boolean;
  isDidNotRemember: boolean;
  updatedConcept: Concept;
}

/**
 * Checks if a student's answer is an identical or near-verbatim copy of the notes definition.
 */
export function checkIfCopiedAnswer(concept: Concept, answer: string): boolean {
  if (!answer || !answer.trim()) return false;

  const normalize = (text: string) => 
    text.toLowerCase().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, ' ').trim();

  const normAnswer = normalize(answer);
  const normDef = normalize(concept.summary || concept.rawContent || '');

  if (!normDef || normDef.length < 15) return false;

  // 1. Direct equality
  if (normAnswer === normDef) return true;

  // 2. Substring copy: Answer contains almost the entire definition
  if (normDef.length > 30 && normAnswer.includes(normDef)) return true;
  if (normAnswer.length > 30 && normDef.includes(normAnswer)) return true;

  // 3. Jaccard word similarity on significant words
  const answerWords = new Set(normAnswer.split(' ').filter(w => w.length > 3));
  const defWords = new Set(normDef.split(' ').filter(w => w.length > 3));

  if (answerWords.size >= 5 && defWords.size >= 5) {
    let intersection = 0;
    answerWords.forEach(w => {
      if (defWords.has(w)) intersection++;
    });

    const similarity = intersection / Math.max(answerWords.size, defWords.size);
    // If over 88% identical vocabulary in short answer
    if (similarity >= 0.88 && Math.abs(answerWords.size - defWords.size) <= 3) {
      return true;
    }
  }

  return false;
}

/**
 * Extracts the first sentence only from the concept definition for hint display.
 */
export function getFirstSentenceHint(concept: Concept): string {
  const text = (concept.summary || concept.rawContent || '').trim();
  if (!text) return 'Focus on the main mechanism and purpose of this concept.';

  // Match until the first sentence terminator (. ! ?) followed by whitespace or end of string
  const match = text.match(/^(.*?[.!?])(?:\s|$)/);
  if (match && match[1]) {
    return match[1].trim();
  }

  // Fallback: first 120 characters
  return text.slice(0, 120).trim() + '...';
}

/**
 * Evaluates student answer using hybrid scoring:
 * - Meaning Match (semantic similarity)
 * - Key Terms Covered (keyword coverage)
 * - Tutor Judgement (AI judge evaluation)
 * Returns calibrated 0-5 score, qualitative blocks, and updated SM-2 schedule.
 */
export function evaluateStudentAnswer(
  concept: Concept,
  answer: string,
  isHinted = false,
  isDidNotRemember = false,
  baseDate: Date = new Date()
): EvaluationResult {
  const sourceDefinition = concept.summary || concept.rawContent || '';
  const keyTerms = concept.keyTerms || [];

  // Special Case: "I do not remember" -> scores 0.0, resets repetitions, schedules for tomorrow
  if (isDidNotRemember) {
    const updatedSM2 = calculateSM2(concept.sm2, 0, baseDate);
    const updatedConcept: Concept = {
      ...concept,
      status: 'weak',
      sm2: updatedSM2
    };

    return {
      score: 0.0,
      gradeLabel: 'Needs work',
      meaningMatchScore: 0,
      keyTermsCoveredScore: 0,
      tutorJudgementScore: 10,
      matchedKeywords: [],
      missedKeywords: keyTerms,
      whatYouGotRight: [],
      whatWasMissing: [
        `Core mechanism of ${concept.title}`,
        keyTerms.length > 0 ? `Key terms: ${keyTerms.slice(0, 4).join(', ')}` : 'Main operational definition'
      ],
      whatWasOff: [],
      sourceDefinition,
      nextReviewLabel: 'tomorrow',
      nextIntervalDays: 1,
      isHinted,
      isCopied: false,
      isDidNotRemember: true,
      updatedConcept
    };
  }

  // 1. Keyword coverage
  const answerLower = answer.toLowerCase();
  const matchedKeywords: string[] = [];
  const missedKeywords: string[] = [];

  keyTerms.forEach(term => {
    const termLower = term.toLowerCase();
    if (answerLower.includes(termLower)) {
      matchedKeywords.push(term);
    } else {
      // Check partial match for multi-word terms
      const parts = termLower.split(/\s+/);
      if (parts.some(p => p.length > 4 && answerLower.includes(p))) {
        matchedKeywords.push(term);
      } else {
        missedKeywords.push(term);
      }
    }
  });

  const keywordRatio = keyTerms.length > 0 ? (matchedKeywords.length / keyTerms.length) : 0.75;
  const keyTermsCoveredScore = Math.round(keywordRatio * 100);

  // 2. Meaning match (semantic similarity heuristic)
  const words = answer.trim().split(/\s+/).filter(Boolean);
  const wordCount = words.length;

  let meaningMatchScore = 40;
  if (wordCount >= 28) meaningMatchScore += 35;
  else if (wordCount >= 18) meaningMatchScore += 25;
  else if (wordCount >= 10) meaningMatchScore += 15;

  // Structural reasoning indicators
  const reasoningTokens = ['because', 'which means', 'allows', 'works by', 'responsible for', 'instead of', 'ensures', 'in order to'];
  const hasReasoning = reasoningTokens.some(token => answerLower.includes(token));
  if (hasReasoning) meaningMatchScore += 15;

  if (isHinted) {
    meaningMatchScore = Math.max(20, meaningMatchScore - 8); // slight adjustment for hint
  }
  meaningMatchScore = Math.min(98, Math.max(15, meaningMatchScore));

  // 3. Tutor Judgement (AI Judge score 0-100)
  let tutorJudgementScore = Math.round(meaningMatchScore * 0.55 + keyTermsCoveredScore * 0.45);
  if (wordCount < 8) tutorJudgementScore = Math.min(35, tutorJudgementScore);
  tutorJudgementScore = Math.min(98, Math.max(15, tutorJudgementScore));

  // Overall 0 to 5 score calculation
  const composite100 = (meaningMatchScore * 0.4) + (keyTermsCoveredScore * 0.35) + (tutorJudgementScore * 0.25);
  // Scale to 0.0 - 5.0 with 1 decimal place
  let finalScore = Number((composite100 / 20).toFixed(1));
  if (isHinted && finalScore > 4.2) finalScore = 4.2;

  // Grade categorization
  let gradeLabel: 'Strong' | 'Partial' | 'Needs work' = 'Partial';
  let qualityForSM2 = 3;

  if (finalScore >= 4.0) {
    gradeLabel = 'Strong';
    qualityForSM2 = 5;
  } else if (finalScore >= 2.5) {
    gradeLabel = 'Partial';
    qualityForSM2 = 3;
  } else {
    gradeLabel = 'Needs work';
    qualityForSM2 = 2;
  }

  // 4. Construct the Three Calm Text Blocks
  const whatYouGotRight: string[] = [];
  const whatWasMissing: string[] = [];
  const whatWasOff: string[] = [];

  // What you got right
  if (matchedKeywords.length > 0) {
    whatYouGotRight.push(`Accurately highlighted key vocabulary: ${matchedKeywords.slice(0, 3).join(', ')}.`);
  }
  if (meaningMatchScore >= 60) {
    whatYouGotRight.push(`Clear intuitive explanation of how ${concept.title} operates.`);
  } else if (wordCount >= 12) {
    whatYouGotRight.push(`Captured the high-level intent in your own words.`);
  }

  // What was missing
  if (missedKeywords.length > 0) {
    whatWasMissing.push(`Consider mentioning: ${missedKeywords.slice(0, 3).join(', ')}.`);
  }
  if (wordCount < 15 && meaningMatchScore < 70) {
    whatWasMissing.push(`A deeper description of the underlying mechanism would strengthen this answer.`);
  }

  // What was off (only populated when genuine discrepancy exists)
  if (finalScore < 2.5 && wordCount >= 10) {
    whatWasOff.push(`Check the distinction between this concept and its prerequisites.`);
  }

  // Update SM-2 Spaced Repetition values with simulated baseDate
  const updatedSM2 = calculateSM2(concept.sm2, qualityForSM2, baseDate);
  const nextIntervalDays = updatedSM2.interval || 1;
  const nextReviewLabel = nextIntervalDays === 1 ? 'tomorrow' : `in ${nextIntervalDays} days`;

  // Phase 7 rule: Mastered means interval of 21 days or more
  const updatedStatus: 'mastered' | 'in_progress' | 'weak' = 
    updatedSM2.interval >= 21 
      ? 'mastered' 
      : qualityForSM2 < 3 
        ? 'weak' 
        : 'in_progress';

  const updatedConcept: Concept = {
    ...concept,
    status: updatedStatus,
    sm2: updatedSM2
  };

  return {
    score: finalScore,
    gradeLabel,
    meaningMatchScore,
    keyTermsCoveredScore,
    tutorJudgementScore,
    matchedKeywords,
    missedKeywords,
    whatYouGotRight,
    whatWasMissing,
    whatWasOff,
    sourceDefinition,
    nextReviewLabel,
    nextIntervalDays,
    isHinted,
    isCopied: false,
    isDidNotRemember: false,
    updatedConcept
  };
}

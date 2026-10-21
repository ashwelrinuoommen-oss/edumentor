import type { Concept } from '../services/mockService';

/**
 * Validates whether adding a prerequisite edge from `newPrereqId` to `targetConceptId`
 * would introduce a directed cycle in the learning dependency graph.
 *
 * In EduMentor's DAG:
 *   If B has A as a prerequisite, the dependency edge is A → B (A must be learned before B).
 *   Adding `newPrereqId` as a prerequisite to `targetConceptId` introduces the edge:
 *     newPrereqId → targetConceptId
 *
 * A cycle would be created if `targetConceptId` can ALREADY reach `newPrereqId` through
 * existing dependent paths (i.e. targetConceptId → ... → newPrereqId).
 */
export function wouldCreateCycle(
  concepts: Concept[],
  targetConceptId: string,
  newPrereqId: string
): boolean {
  // Self-loop
  if (targetConceptId === newPrereqId) {
    return true;
  }

  // Check if targetConceptId can reach newPrereqId
  const visited = new Set<string>();
  const queue: string[] = [targetConceptId];

  while (queue.length > 0) {
    const currId = queue.shift()!;
    if (currId === newPrereqId) {
      return true; // Path exists! Adding newPrereqId -> targetConceptId would form a loop.
    }
    visited.add(currId);

    // Find all concepts that directly list currId as a prerequisite
    const directDependents = concepts.filter(c => (c.prerequisiteIds || []).includes(currId));
    for (const dep of directDependents) {
      if (!visited.has(dep.id)) {
        queue.push(dep.id);
      }
    }
  }

  return false;
}

/**
 * Re-orders concepts in topological prerequisite order (Kahn's Algorithm)
 * and updates order indices and difficulties.
 */
export function reorderConceptsWithPrerequisites(concepts: Concept[]): Concept[] {
  if (concepts.length <= 1) return concepts;

  const conceptMap = new Map<string, Concept>();
  concepts.forEach(c => conceptMap.set(c.id, { ...c }));

  // In-degree map & adjacency list (prereqId -> dependentIds)
  const inDegree = new Map<string, number>();
  const adjacency = new Map<string, string[]>();

  concepts.forEach(c => {
    // Only count prerequisites that actually exist in the current concept list
    const validPrereqIds = (c.prerequisiteIds || []).filter(pId => conceptMap.has(pId));
    inDegree.set(c.id, validPrereqIds.length);
    adjacency.set(c.id, []);
  });

  // Populate adjacency: for each concept C and its prereq P, edge is P -> C
  concepts.forEach(c => {
    const validPrereqIds = (c.prerequisiteIds || []).filter(pId => conceptMap.has(pId));
    validPrereqIds.forEach(pId => {
      adjacency.get(pId)?.push(c.id);
    });
  });

  // Queue of nodes with 0 in-degree
  const queue: string[] = [];
  concepts.forEach(c => {
    if (inDegree.get(c.id) === 0) {
      queue.push(c.id);
    }
  });

  const sortedIds: string[] = [];
  while (queue.length > 0) {
    const currId = queue.shift()!;
    sortedIds.push(currId);

    const dependents = adjacency.get(currId) || [];
    for (const depId of dependents) {
      const currentIn = inDegree.get(depId) || 0;
      const nextIn = currentIn - 1;
      inDegree.set(depId, nextIn);
      if (nextIn === 0) {
        queue.push(depId);
      }
    }
  }

  // Handle any nodes in a cycle or left out
  if (sortedIds.length < concepts.length) {
    concepts.forEach(c => {
      if (!sortedIds.includes(c.id)) {
        sortedIds.push(c.id);
      }
    });
  }

  // Map to concept array with re-indexed order
  return sortedIds.map((id, index) => {
    const item = conceptMap.get(id)!;
    const prereqCount = (item.prerequisiteIds || []).length;
    let difficulty: 'Beginner' | 'Intermediate' | 'Advanced' = 'Beginner';

    if (prereqCount >= 2 || index >= Math.floor(sortedIds.length * 0.65)) {
      difficulty = 'Advanced';
    } else if (prereqCount === 1 || index >= Math.floor(sortedIds.length * 0.35)) {
      difficulty = 'Intermediate';
    }

    return {
      ...item,
      orderIndex: index + 1,
      difficulty
    };
  });
}

/**
 * Helper to get prerequisite concepts for a given concept
 */
export function getPrerequisitesForConcept(concept: Concept, allConcepts: Concept[]): Concept[] {
  const prereqIds = new Set(concept.prerequisiteIds || []);
  return allConcepts.filter(c => prereqIds.has(c.id));
}

/**
 * Helper to get dependent concepts (concepts that require this concept)
 */
export function getDependentsForConcept(concept: Concept, allConcepts: Concept[]): Concept[] {
  return allConcepts.filter(c => (c.prerequisiteIds || []).includes(concept.id));
}

/**
 * LocalStorage Persistence Service for EduMentor
 * Handles decks, concepts, study session state, and spaced repetition queues.
 */

import { SAMPLE_NOTE_SETS } from '../data/sampleNotes';
import { extractConceptsFromText } from './conceptExtractor';

const STORAGE_KEY_DECKS = 'edumentor_decks_v1';
const STORAGE_KEY_ACTIVE_ID = 'edumentor_active_deck_id';

/**
 * Initializes default decks if none exist in localStorage
 */
export function initializeStorage() {
  try {
    const existing = localStorage.getItem(STORAGE_KEY_DECKS);
    if (!existing) {
      // Seed with sample note decks
      const initialDecks = SAMPLE_NOTE_SETS.map(sample => {
        const concepts = extractConceptsFromText(sample.content, sample.title);
        return {
          id: sample.id,
          title: sample.title,
          category: sample.category,
          icon: sample.icon,
          description: sample.description,
          rawNotes: sample.content,
          concepts: concepts,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
      });

      localStorage.setItem(STORAGE_KEY_DECKS, JSON.stringify(initialDecks));
      localStorage.setItem(STORAGE_KEY_ACTIVE_ID, initialDecks[0].id);
      return { decks: initialDecks, activeId: initialDecks[0].id };
    }

    const decks = JSON.parse(existing);
    const activeId = localStorage.getItem(STORAGE_KEY_ACTIVE_ID) || (decks[0] ? decks[0].id : null);
    return { decks, activeId };
  } catch (err) {
    console.error('Failed to access localStorage, returning fallback memory state:', err);
    return { decks: [], activeId: null };
  }
}

/**
 * Retrieves all stored decks
 */
export function loadAllDecks() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_DECKS);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error('Error loading decks:', e);
    return [];
  }
}

/**
 * Saves all decks to storage
 */
export function saveDecks(decks) {
  try {
    localStorage.setItem(STORAGE_KEY_DECKS, JSON.stringify(decks));
  } catch (e) {
    console.error('Error saving decks to localStorage:', e);
  }
}

/**
 * Saves or updates a single deck
 */
export function saveDeck(deck) {
  const decks = loadAllDecks();
  const index = decks.findIndex(d => d.id === deck.id);
  
  if (index >= 0) {
    decks[index] = { ...deck, updatedAt: new Date().toISOString() };
  } else {
    decks.unshift({ ...deck, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() });
  }

  saveDecks(decks);
  return decks;
}

/**
 * Deletes a deck
 */
export function deleteDeck(deckId) {
  const decks = loadAllDecks().filter(d => d.id !== deckId);
  saveDecks(decks);
  return decks;
}

/**
 * Updates a concept within a specific deck
 */
export function updateConceptInDeck(deckId, updatedConcept) {
  const decks = loadAllDecks();
  const deck = decks.find(d => d.id === deckId);
  if (!deck) return decks;

  deck.concepts = deck.concepts.map(c => c.id === updatedConcept.id ? updatedConcept : c);
  deck.updatedAt = new Date().toISOString();
  saveDecks(decks);
  return decks;
}

import { create } from 'zustand';

const useEmotionStore = create((set) => ({
  emotion: null,
  confidence: null,
  setEmotion: (emotion, confidence) => set({ emotion, confidence }),
}));

export default useEmotionStore;

import { create } from 'zustand';
import { getDiaryList, summarizeAndSaveDiary } from '../api/diary';

const useDiaryStore = create((set) => ({
  diaryEntries: [], 
  summary: null, 
  loading: false, 
  error: null, 

  setDiaryEntries: (entries) => set({ diaryEntries: entries }),
  setSummary: (summary) => set({ summary }),
  setLoading: (isLoading) => set({ loading: isLoading }),
  setError: (error) => set({ error }),

  // 일기 목록 가져오기
  fetchDiaryList: async (date) => {
    set({ loading: true, error: null });
    try {
      const response = await getDiaryList(date);
      set({ diaryEntries: response.diaries || [], loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  // 채팅 종료 후 요약 생성 및 저장
  generateSummaryAndSave: async (chatroomId) => {
    set({ loading: true, error: null });
    try {
      const response = await summarizeAndSaveDiary(chatroomId);
      set({ summary: response.summary, loading: false });

      // 일기 목록에 새 데이터 추가
      set((state) => ({
        diaryEntries: [
          ...state.diaryEntries,
          {
            chatroom_id: chatroomId,
            content: response.summary,
            emotion: response.emotion || null,
            date: response.date || new Date().toISOString().split('T')[0],
          },
        ],
      }));

    } catch (error) {
      set({ error: error.message, loading: false });
    }
  }
}));

export default useDiaryStore;

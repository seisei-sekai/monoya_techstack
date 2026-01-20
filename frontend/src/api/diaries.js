import apiClient from "./client";

export const diaryApi = {
  // Get all diaries for the current user
  getAll: async () => {
    const response = await apiClient.get("/diaries");
    return response.data;
  },

  // Get a single diary by ID
  getById: async (id) => {
    const response = await apiClient.get(`/diaries/${id}`);
    return response.data;
  },

  // Create a new diary
  create: async (diary) => {
    const response = await apiClient.post("/diaries", diary);
    return response.data;
  },

  // Update a diary
  update: async (id, diary) => {
    const response = await apiClient.put(`/diaries/${id}`, diary);
    return response.data;
  },

  // Delete a diary
  delete: async (id) => {
    await apiClient.delete(`/diaries/${id}`);
  },

  // Get AI insight for a diary
  getAiInsight: async (id) => {
    const response = await apiClient.post(`/diaries/${id}/ai-insight`);
    return response.data;
  },
};

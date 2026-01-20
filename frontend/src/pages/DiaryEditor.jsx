import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { diaryApi } from "../api/diaries";
import toast from "react-hot-toast";
import { ArrowLeft, Save, Sparkles, Lightbulb } from "lucide-react";
import apiClient from "../api/client";

export default function DiaryEditor() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = Boolean(id && id !== "new");

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [aiInsight, setAiInsight] = useState("");
  const [llamaRecommendation, setLlamaRecommendation] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingInsight, setLoadingInsight] = useState(false);
  const [loadingRecommendation, setLoadingRecommendation] = useState(false);

  useEffect(() => {
    if (isEditing && id) {
      loadDiary(id);
    }
  }, [id, isEditing]);

  const loadDiary = async (diaryId) => {
    try {
      const diary = await diaryApi.getById(diaryId);
      setTitle(diary.title);
      setContent(diary.content);
      setAiInsight(diary.aiInsight || "");
    } catch (error) {
      toast.error("Failed to load diary");
      navigate("/dashboard");
    }
  };

  const handleSave = async () => {
    if (!title.trim() || !content.trim()) {
      toast.error("Please fill in both title and content");
      return;
    }

    setLoading(true);
    try {
      if (isEditing && id) {
        await diaryApi.update(id, { title, content });
        toast.success("Diary updated successfully");
      } else {
        await diaryApi.create({ title, content });
        toast.success("Diary created successfully");
      }
      navigate("/dashboard");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to save diary");
    } finally {
      setLoading(false);
    }
  };

  const handleGetAiInsight = async () => {
    if (!isEditing || !id) {
      toast.error("Please save the diary first");
      return;
    }

    setLoadingInsight(true);
    try {
      const result = await diaryApi.getAiInsight(id);
      setAiInsight(result.insight);
      toast.success("AI insight generated!");
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to generate AI insight"
      );
    } finally {
      setLoadingInsight(false);
    }
  };

  const handleGetLlamaRecommendation = async () => {
    if (!content.trim()) {
      toast.error("请先写一些内容");
      return;
    }

    setLoadingRecommendation(true);
    try {
      const response = await apiClient.post("/diaries/recommend", {
        title: title,
        content: content,
      });
      setLlamaRecommendation(response.data.insight);
      toast.success("Llama 推荐生成成功！");
    } catch (error) {
      const errorMsg =
        error.response?.data?.detail || "Failed to generate recommendation";
      if (errorMsg.includes("Ollama")) {
        toast.error(errorMsg, { duration: 5000 });
      } else {
        toast.error(errorMsg);
      }
    } finally {
      setLoadingRecommendation(false);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="bg-white shadow-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate("/dashboard")}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition"
            >
              <ArrowLeft className="h-5 w-5" />
              Back to Dashboard
            </button>
            <div className="flex gap-3">
              {isEditing && (
                <button
                  onClick={handleGetAiInsight}
                  disabled={loadingInsight}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                >
                  <Sparkles className="h-4 w-4" />
                  {loadingInsight ? "Generating..." : "Get AI Insight"}
                </button>
              )}
              <button
                onClick={handleSave}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
              >
                <Save className="h-4 w-4" />
                {loading ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-6">
            <label
              htmlFor="title"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Title
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-3 text-2xl font-semibold border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Enter diary title..."
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="content"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Content
            </label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={15}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              placeholder="Write your thoughts here..."
            />
          </div>

          {/* Llama 推荐按钮 */}
          <div className="mb-6">
            <button
              onClick={handleGetLlamaRecommendation}
              disabled={loadingRecommendation || !content.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-lg hover:from-green-600 hover:to-teal-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Lightbulb className="h-4 w-4" />
              {loadingRecommendation ? "生成中..." : "🦙 获取 Llama 写作建议"}
            </button>
          </div>

          {llamaRecommendation && (
            <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl p-6 border border-green-200 mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb className="h-5 w-5 text-green-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  🦙 Llama 写作建议
                </h3>
              </div>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {llamaRecommendation}
              </p>
            </div>
          )}

          {aiInsight && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  AI Insight
                </h3>
              </div>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {aiInsight}
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

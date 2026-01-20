import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { auth } from "../config/firebase";
import { diaryApi } from "../api/diaries";
import toast from "react-hot-toast";
import {
  Plus,
  LogOut,
  BookOpen,
  Trash2,
  Edit,
  Calendar,
  LayoutGrid,
} from "lucide-react";
import { format } from "date-fns";

export default function Dashboard() {
  const navigate = useNavigate();
  const [diaries, setDiaries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDiaries();
  }, []);

  const loadDiaries = async () => {
    try {
      const data = await diaryApi.getAll();
      setDiaries(data);
    } catch (error) {
      toast.error("Failed to load diaries");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this diary?")) return;

    try {
      await diaryApi.delete(id);
      setDiaries(diaries.filter((d) => d.id !== id));
      toast.success("Diary deleted successfully");
    } catch (error) {
      toast.error("Failed to delete diary");
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      toast.success("Logged out successfully");
    } catch (error) {
      toast.error("Failed to log out");
    }
  };

  return (
    <div className="min-h-screen">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">AI Diary</h1>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate("/xdf-class-arranger")}
                className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                <LayoutGrid className="h-4 w-4" />
                Class Arranger
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-gray-900">My Diaries</h2>
          <button
            onClick={() => navigate("/diary/new")}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            <Plus className="h-5 w-5" />
            New Entry
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-gray-600">Loading your diaries...</div>
          </div>
        ) : diaries.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl shadow">
            <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              No diaries yet
            </h3>
            <p className="text-gray-600 mb-6">
              Start writing your first diary entry!
            </p>
            <button
              onClick={() => navigate("/diary/new")}
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              <Plus className="h-5 w-5" />
              Create First Entry
            </button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {diaries.map((diary) => (
              <div
                key={diary.id}
                className="bg-white rounded-xl shadow-md hover:shadow-lg transition p-6"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-xl font-semibold text-gray-900 flex-1">
                    {diary.title}
                  </h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/diary/${diary.id}`)}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(diary.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <p className="text-gray-600 line-clamp-3 mb-4">
                  {diary.content}
                </p>

                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar className="h-4 w-4" />
                  {format(new Date(diary.createdAt), "MMM d, yyyy")}
                </div>

                {diary.aiInsight && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-900 font-medium">
                      AI Insight:
                    </p>
                    <p className="text-sm text-blue-800 mt-1">
                      {diary.aiInsight}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { useAuthStore } from "./store/authStore";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import DiaryEditor from "./pages/DiaryEditor";
import XdfLayout from "./XdfClassArranger/XdfLayout.jsx";
import XdfDashboard from "./XdfClassArranger/Dashboard/Dashboard.jsx";
import XdfFunction from "./XdfClassArranger/Function/Function.jsx";
import XdfMyPage from "./XdfClassArranger/MyPage/MyPage.jsx";
import { useEffect } from "react";
import { auth } from "./config/firebase";

function App() {
  const { user, setUser, loading, setLoading } = useAuthStore();

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((firebaseUser) => {
      setUser(firebaseUser);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [setUser, setLoading]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-xl text-gray-700">Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Toaster position="top-right" />
        <Routes>
          <Route
            path="/login"
            element={user ? <Navigate to="/dashboard" /> : <Login />}
          />
          <Route
            path="/dashboard"
            element={user ? <Dashboard /> : <Navigate to="/login" />}
          />
          <Route
            path="/diary/new"
            element={user ? <DiaryEditor /> : <Navigate to="/login" />}
          />
          <Route
            path="/diary/:id"
            element={user ? <DiaryEditor /> : <Navigate to="/login" />}
          />
          {/* XdfClassArranger 路由 */}
          <Route
            path="/xdf-class-arranger"
            element={user ? <XdfLayout /> : <Navigate to="/login" />}
          >
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<XdfDashboard />} />
            <Route path="function" element={<XdfFunction />} />
            <Route path="mypage" element={<XdfMyPage />} />
          </Route>
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

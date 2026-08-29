import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/** Gates a route behind an authenticated Supabase session (Section 8.2/9.4:
 * "blocks access to chat until authenticated"). */
export default function ProtectedRoute({ children }) {
  const { session, loading } = useAuth();

  if (loading) {
    return null;
  }
  if (!session) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { session, loading, signIn, signUp } = useAuth();
  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [checkEmail, setCheckEmail] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  if (!loading && session) {
    return <Navigate to="/chat" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setCheckEmail(false);
    setSubmitting(true);
    try {
      if (mode === "signin") {
        const { error: signInError } = await signIn(email, password);
        if (signInError) throw signInError;
      } else {
        const { data, error: signUpError } = await signUp(email, password);
        if (signUpError) throw signUpError;
        // Email confirmation is enabled on this project — signUp succeeds
        // but returns no session until the user clicks the confirmation
        // link, so there's nothing to redirect to yet.
        if (!data.session) {
          setCheckEmail(true);
        }
      }
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-cream px-4">
      <div className="w-full max-w-sm rounded-lg bg-white p-8 shadow-sm">
        <h1 className="text-center text-2xl font-semibold text-navy">ConstituteAI</h1>
        <p className="mt-1 text-center text-sm text-navy/60">
          Constitutional research assistant
        </p>

        <div className="mt-6 flex rounded-md bg-cream p-1 text-sm font-medium">
          <button
            type="button"
            onClick={() => {
              setMode("signin");
              setError(null);
              setCheckEmail(false);
            }}
            className={`flex-1 rounded py-1.5 transition ${
              mode === "signin" ? "bg-white text-navy shadow-sm" : "text-navy/60"
            }`}
          >
            Sign in
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("signup");
              setError(null);
              setCheckEmail(false);
            }}
            className={`flex-1 rounded py-1.5 transition ${
              mode === "signup" ? "bg-white text-navy shadow-sm" : "text-navy/60"
            }`}
          >
            Sign up
          </button>
        </div>

        {checkEmail ? (
          <p className="mt-6 rounded-md bg-amber/10 p-3 text-sm text-navy">
            Check your email to confirm your account, then sign in.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-navy">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-1 w-full rounded-md border border-navy/20 px-3 py-2 text-sm focus:border-navy focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-navy">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="mt-1 w-full rounded-md border border-navy/20 px-3 py-2 text-sm focus:border-navy focus:outline-none"
              />
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-full bg-amber py-2 text-sm font-semibold text-white transition hover:bg-amber/90 disabled:opacity-60"
            >
              {submitting ? "Please wait…" : mode === "signin" ? "Sign in" : "Sign up"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

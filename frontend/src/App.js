import React, { useState } from "react";
import axios from "axios";
import "./App.css";

import { auth } from "./firebase";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
} from "firebase/auth";

/**
 * 8 questions breakdown:
 *   Q1–Q3 : Theory            (Easy)
 *   Q4–Q6 : Coding/Practical  (Medium)  ← "Coding" if tech topic, else "Practical"
 *   Q7–Q8 : Scenario          (Hard)
 */
const QUESTION_META = [
  { type: "Theory",   difficulty: "Easy",   color: "var(--success)" },
  { type: "Theory",   difficulty: "Easy",   color: "var(--success)" },
  { type: "Theory",   difficulty: "Easy",   color: "var(--success)" },
  { type: "Coding",   difficulty: "Medium", color: "var(--accent)"  },
  { type: "Coding",   difficulty: "Medium", color: "var(--accent)"  },
  { type: "Coding",   difficulty: "Medium", color: "var(--accent)"  },
  { type: "Scenario", difficulty: "Hard",   color: "var(--danger)"  },
  { type: "Scenario", difficulty: "Hard",   color: "var(--danger)"  },
];

const TYPE_ICON = {
  Theory:    "📖",
  Coding:    "💻",
  Practical: "🛠️",
  Scenario:  "🧩",
};

const TOTAL_QUESTIONS = 8;

function App() {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser]         = useState(null);

  const [step, setStep]                   = useState("topic");
  const [topic, setTopic]                 = useState("");
  const [isCodingTopic, setIsCodingTopic] = useState(true);
  const [questions, setQuestions]         = useState([]);
  const [answers, setAnswers]             = useState([]);
  const [currentIndex, setCurrentIndex]   = useState(0);
  const [result, setResult]               = useState(null);
  const [history, setHistory]             = useState([]);
  const [loading, setLoading]             = useState(false);

  const backendURL = "http://127.0.0.1:8000";

  // Swap "Coding" → "Practical" for non-technical topics
  const resolveType = (rawType) =>
    rawType === "Coding" && !isCodingTopic ? "Practical" : rawType;

  // Get plain question string (backend may return object or string)
  const getQuestionText = (q) => (typeof q === "object" ? q.question : q);

  // ---------------- AUTH ----------------

  const handleSignup = async () => {
    try {
      const res = await createUserWithEmailAndPassword(auth, email, password);
      setUser(res.user);
    } catch (err) { alert(err.message); }
  };

  const handleLogin = async () => {
    try {
      const res = await signInWithEmailAndPassword(auth, email, password);
      setUser(res.user);
    } catch (err) { alert(err.message); }
  };

  const handleLogout = async () => {
    await signOut(auth);
    setUser(null);
    setHistory([]);
    setResult(null);
    setStep("topic");
    setTopic("");
    setQuestions([]);
    setAnswers([]);
    setCurrentIndex(0);
  };

  // ---------------- INTERVIEW ----------------

  // Step 1 → fetch 8 mixed, progressive questions
  const handleStart = async () => {
    if (!topic.trim()) return alert("Please enter a topic!");
    setLoading(true);
    try {
      const res = await axios.post(`${backendURL}/get_questions`, {
        topic,
        count: TOTAL_QUESTIONS,
        difficulty: "progressive",          // easy(3) → medium(3) → hard(2)
        types: ["theory", "coding", "scenario"], // backend swaps "coding"→"practical" if needed
      });

      const qs       = res.data.questions;        // array of strings or {question, type}
      const isCoding = res.data.is_coding_topic ?? true; // boolean from backend

      setQuestions(qs);
      setIsCodingTopic(isCoding);
      setAnswers(new Array(qs.length).fill(""));
      setCurrentIndex(0);
      setStep("answering");
    } catch (err) {
      console.error(err);
      alert("Error fetching questions");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (value) => {
    const updated = [...answers];
    updated[currentIndex] = value;
    setAnswers(updated);
  };

  const handleNext = () => {
    if (!answers[currentIndex].trim()) return alert("Please answer before continuing!");
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${backendURL}/start_interview`, {
        user_id:   user?.uid || "guest",
        topic,
        questions: questions.map(getQuestionText),
        answers,
      });
      setResult(res.data.history);
      setStep("results");
    } catch (err) {
      console.error(err);
      alert("Error submitting answers");
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = () => {
    setStep("topic");
    setTopic("");
    setQuestions([]);
    setAnswers([]);
    setCurrentIndex(0);
    setResult(null);
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${backendURL}/history/${user.uid}`);
      setHistory(res.data.history);
    } catch (err) {
      console.error(err);
      alert("Error fetching history");
    }
  };

  // Derived UI values for the answering step
  const totalQ          = questions.length || TOTAL_QUESTIONS;
  const progressPercent = step === "answering"
    ? Math.round(((currentIndex + 1) / totalQ) * 100)
    : 0;
  const meta      = QUESTION_META[currentIndex] || QUESTION_META[0];
  const typeLabel = resolveType(meta.type);
  const typeIcon  = TYPE_ICON[typeLabel] || "❓";

  return (
    <div>
      {/* SIDEBAR */}
      <div className="sidebar">
        <h2>Account</h2>
        {!user ? (
          <>
            <input
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleLogin}>Login</button>
            <button onClick={handleSignup}>Signup</button>
            <p style={{ marginTop: "10px" }}>OR</p>
            <button onClick={() => setUser("guest")}>Continue as Guest</button>
          </>
        ) : (
          <>
            <p>Logged in as {user === "guest" ? "Guest" : user.email}</p>
            <button onClick={handleLogout}>Logout</button>
          </>
        )}
      </div>

      {/* MAIN CONTENT */}
      <div className="container">
        <h1>🤖 AI Interview System</h1>

        {/* ── STEP 1: Topic ── */}
        {step === "topic" && (
          <>
            <p className="step-label">Step 1 — Choose a topic</p>
            <input
              placeholder="Enter Topic (e.g., DSA, ML, React, Product Management)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleStart()}
            />
            <button onClick={handleStart} disabled={loading}>
              {loading ? "Generating Questions..." : "Start Interview →"}
            </button>

            {/* Structure legend */}
            <div className="type-legend">
              <span style={{ color: "var(--success)" }}>📖 Theory (Q1–Q3)</span>
              &nbsp;·&nbsp;
              <span style={{ color: "var(--accent)" }}>💻 Coding / 🛠️ Practical (Q4–Q6)</span>
              &nbsp;·&nbsp;
              <span style={{ color: "var(--danger)" }}>🧩 Scenario (Q7–Q8)</span>
            </div>
          </>
        )}

        {/* ── STEP 2: One Question at a Time ── */}
        {step === "answering" && questions.length > 0 && (
          <>
            <p className="step-label">Step 2 — Answer the questions</p>

            {/* Progress bar */}
            <div className="progress-wrap">
              <div
                className="progress-bar"
                style={{ width: `${progressPercent}%`, background: meta.color }}
              />
            </div>
            <p className="progress-label">
              Question {currentIndex + 1} of {questions.length}
            </p>

            {/* Badges */}
            <div className="badge-row">
              <span className="difficulty-badge" style={{ background: meta.color }}>
                {meta.difficulty}
              </span>
              <span className="type-badge" style={{ borderColor: meta.color, color: meta.color }}>
                {typeIcon} {typeLabel}
              </span>
            </div>

            {/* Question card */}
            <div className="question-block">
              <p className="question-text">
                <b>Q{currentIndex + 1}:</b> {getQuestionText(questions[currentIndex])}
              </p>
              <textarea
                placeholder={
                  typeLabel === "Coding"
                    ? "Write your code or pseudocode here..."
                    : typeLabel === "Practical"
                    ? "Describe your approach or steps..."
                    : typeLabel === "Scenario"
                    ? "Walk through how you'd handle this situation..."
                    : "Your answer..."
                }
                value={answers[currentIndex]}
                onChange={(e) => handleAnswerChange(e.target.value)}
                rows={typeLabel === "Coding" ? 8 : 5}
                style={
                  typeLabel === "Coding"
                    ? { fontFamily: "monospace", fontSize: "0.9rem" }
                    : {}
                }
              />
            </div>

            {/* Navigation */}
            <div className="button-row">
              <button
                className="btn-secondary"
                onClick={handlePrev}
                disabled={currentIndex === 0}
              >
                ← Prev
              </button>
              <button
                className="btn-primary"
                onClick={handleNext}
                disabled={loading}
              >
                {loading
                  ? "Submitting..."
                  : currentIndex === questions.length - 1
                  ? "Submit Answers →"
                  : "Next →"}
              </button>
              <button className="btn-ghost" onClick={handleRestart}>
                ✕ Start Over
              </button>
            </div>
          </>
        )}

        {/* ── STEP 3: Results ── */}
        {step === "results" && result && (
          <>
            <p className="step-label">Step 3 — Your Results</p>

            {/* Summary banner */}
            <div className="summary-banner">
              <span>Total Score: </span>
              <strong>
                {result.reduce((sum, r) => sum + r.score, 0)} / {result.length * 10}
              </strong>
              <span style={{ marginLeft: "16px", color: "var(--muted)", fontSize: "0.85rem" }}>
                ({result.length} questions · {isCodingTopic ? "Technical" : "General"} track)
              </span>
            </div>

            <div className="result">
              {result.map((r, i) => {
                const m      = QUESTION_META[i] || QUESTION_META[0];
                const tLabel = resolveType(m.type);
                const tIcon  = TYPE_ICON[tLabel] || "❓";
                return (
                  <div key={i} className="result-card">

                    {/* Header row */}
                    <div className="result-header">
                      <span className="result-badge">Q{i + 1}</span>
                      <span
                        className="type-badge"
                        style={{ borderColor: m.color, color: m.color }}
                      >
                        {tIcon} {tLabel}
                      </span>
                      <span
                        className="difficulty-badge"
                        style={{ background: m.color, marginLeft: "auto" }}
                      >
                        {m.difficulty}
                      </span>
                    </div>

                    {/* Question */}
                    <div className="result-section result-question">
                      <p>{r.question}</p>
                    </div>

                    {/* Your Answer */}
                    <div className="result-section result-answer">
                      <span className="result-label">Your Answer</span>
                      <p
                        style={
                          tLabel === "Coding"
                            ? { fontFamily: "monospace", whiteSpace: "pre-wrap" }
                            : {}
                        }
                      >
                        {r.answer}
                      </p>
                    </div>

                    {/* Score */}
                    <div className="result-section result-score">
                      <span className="result-label">Score</span>
                      <div className="score-bar-wrap">
                        <div
                          className="score-bar"
                          style={{
                            width: `${(r.score / 10) * 100}%`,
                            background:
                              r.score > 7
                                ? "var(--success)"
                                : r.score > 4
                                ? "var(--accent)"
                                : "var(--danger)",
                          }}
                        />
                      </div>
                      <span className="score-number">{r.score} / 10</span>
                    </div>

                    {/* Feedback */}
                    <div className="result-section result-feedback">
                      <span className="result-label">Feedback</span>
                      <div className="feedback-text">
                        {r.feedback.split("\n").map(
                          (line, j) =>
                            line.trim() && (
                              <p key={j}>
                                {line.replace(/\*\*/g, "").replace(/^\* /, "• ")}
                              </p>
                            )
                        )}
                      </div>
                    </div>

                  </div>
                );
              })}
            </div>

            <div className="button-row">
              <button className="btn-primary" onClick={handleRestart}>
                Try Another Topic
              </button>
              {user && user !== "guest" && (
                <button className="btn-secondary" onClick={fetchHistory}>
                  View History
                </button>
              )}
            </div>
          </>
        )}

        {/* ── HISTORY ── */}
        {history.length > 0 && (
          <div className="history">
            <h2>Past Sessions</h2>
            {history.map((h, i) => (
              <div key={i} className="card">
                <p><b>Date:</b> {new Date(h.timestamp).toLocaleString()}</p>
                {h.history.map((q, j) => (
                  <div key={j}>
                    <p><b>Q:</b> {q.question}</p>
                    <p><b>Score:</b> {q.score}</p>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
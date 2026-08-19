import { useEffect, useMemo, useRef, useState } from "react";
import {
  Navigate,
  Route,
  Routes,
  Link,
  useNavigate,
} from "react-router-dom";

import {
  Brain,
  FileText,
  Home,
  LogIn,
  LogOut,
  Menu,
  BarChart3,
  BookOpen,
  Sparkles,
  Upload,
  CheckCircle2,
  ChevronRight,
  Target,
  History,
  X,
  Youtube,
} from "lucide-react";

import api, { setToken } from "./api";
import Feedback from "./Feedback";
import type { Question, User } from "./types";

/* =========================================================
   LAYOUT
========================================================= */

function Layout({
  user,
  logout,
  children,
}: {
  user: User;
  logout: () => void;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  
  const links = [
    ["/dashboard", "Dashboard", Home],
    ["/topics", "Popular Topics", BookOpen],
    ["/upload", "Upload Notes", Upload],
    ["/summarize", "Summarize", FileText],
    ["/progress", "My Progress", BarChart3],
    ["/generate-topic", "Generate from Topic", Sparkles],
    ["/youtube", "YouTube Quiz", Youtube],
    ["/generate-information", "Generate from Information", FileText],
  ] as const;

  return (
    <div className="app-shell">
      <aside className={open ? "sidebar open" : "sidebar"}>
        <div className="brand">
          <div className="brand-icon">
            <Brain size={22} />
          </div>

          <div>
            <b>QuizMate AI</b>
            <span>Learn. Practice. Master.</span>
          </div>
        </div>

        <nav>
          {links.map(([to, label, Icon]) => (
            <Link
              key={to}
              to={to}
              onClick={() => setOpen(false)}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>

        <button className="logout" onClick={logout}>
          <LogOut size={17} />
          Logout
        </button>
      </aside>

      {open && (
        <div
          className="overlay"
          onClick={() => setOpen(false)}
        />
      )}

      <main className="main">
        <header className="topbar">
          <button
            className="menu-btn"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>

          <span>AI-powered study assistant</span>

          <div className="user-chip">
            {user.name.slice(0, 1).toUpperCase()}
          </div>
        </header>

        <div className="content">
          {children}
        </div>
      </main>
    </div>
  );
}

/* =========================================================
   AUTH
========================================================= */

function Auth({
  onLogin,
}: {
  onLogin: (token: string, user: User) => void;
}) {
  const [mode, setMode] =
    useState<"login" | "register">("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("demo@quizmate.ai");
  const [password, setPassword] = useState("demo123");
  const [error, setError] = useState("");

  const nav = useNavigate();

  const submit = async () => {
    try {
      setError("");

      const url =
        mode === "login"
          ? "/api/auth/login"
          : "/api/auth/register";

      const { data } = await api.post(url, {
        name: name || undefined,
        email,
        password,
      });

      onLogin(data.token, data.user);

      nav("/dashboard");
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
          "Something went wrong."
      );
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-art">
        <div className="logo-large">
          <Brain size={34} />
        </div>

        <h1>Learn smarter with AI.</h1>

        <p>
          Turn topics and your own notes into friendly,
          personalized quizzes and revision summaries.
        </p>

        <div className="feature-pills">
          <span>✨ AI Quiz Generator</span>
          <span>📄 PDF Summarizer</span>
          <span>📊 Learning Progress</span>
          <span>🎥 YouTube Quiz Generator</span>
        </div>
      </div>

      <div className="auth-card">
        <div className="mini-brand">
          <Brain size={20} />
          QuizMate AI
        </div>

        <h2>
          {mode === "login"
            ? "Welcome back"
            : "Create your account"}
        </h2>

        <p className="muted">
          {mode === "login"
            ? "Ready for another round?"
            : "Start building your learning streak."}
        </p>

        {mode === "register" && (
          <label>
            Name

            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
            />
          </label>
        )}

        <label>
          Email

          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
        </label>

        <label>
          Password

          <input
            type="password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            placeholder="enter your password here"
          />
        </label>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <button
          className="primary big"
          onClick={submit}
        >
          {mode === "login" ? (
            <>
              <LogIn size={18} />
              Login
            </>
          ) : (
            <>
              <Sparkles size={18} />
              Create Account
            </>
          )}
        </button>

        <button
          className="link-btn"
          onClick={() =>
            setMode(
              mode === "login"
                ? "register"
                : "login"
            )
          }
        >
          {mode === "login"
            ? "New here? Create an account"
            : "Already have an account? Login"}
        </button>

        <div className="demo-note">
          Demo login: demo@quizmate.ai / demo123
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard({ user }: { user: User }) {
  const nav = useNavigate();
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    api.get("/api/results")
      .then((r) => setRows(Array.isArray(r.data) ? r.data : []))
      .catch(() => setRows([]));
  }, []);

  const recent = [...rows].reverse().slice(-7);
  const average = rows.length
    ? Math.round(
        rows.reduce((sum, r) => sum + ((r.score || 0) / Math.max(r.total || 1, 1)) * 100, 0) / rows.length
      )
    : 0;

  return (
    <>
      <div className="hero">
        <div>
          <div className="eyebrow">YOUR PERSONAL AI STUDY SPACE</div>
          <h1>Hello, {user.name}! 👋</h1>
          <p>What would you like to learn today?</p>
        </div>
        <div className="hero-art"><Sparkles size={34} /></div>
      </div>

      {/* Exactly 3 cards in the first row and 3 in the second row. */}
      <div
        className="grid-4 dashboard-actions"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
          gap: "20px",
        }}
      >
        <ActionCard
          icon={<Sparkles />}
          title="Generate from Topic"
          text="Enter any topic and let AI create a fresh quiz."
          button="Enter Topic"
          onClick={() => nav("/generate-topic")}
        />

        <ActionCard
          icon={<Upload />}
          title="Upload Notes"
          text="Turn your PDF or DOCX notes into a personalized quiz."
          button="Upload Notes"
          onClick={() => nav("/upload")}
        />

        <ActionCard
          icon={<Youtube />}
          title="Generate from YouTube"
          text="Paste a YouTube link and create a quiz from its transcript."
          button="Use YouTube"
          onClick={() => nav("/youtube")}
        />

        <ActionCard
          icon={<FileText />}
          title="Generate from Information"
          text="Paste your own information, notes, or study text and generate a quiz."
          button="Enter Information"
          onClick={() => nav("/generate-information")}
        />

        <ActionCard
          icon={<BookOpen />}
          title="Summarize Notes"
          text="Turn long PDF or DOCX study material into quick revision notes."
          button="Summarize"
          onClick={() => nav("/summarize")}
        />

        <ActionCard
          icon={<Target />}
          title="Start Quiz with Popular Topics"
          text="Choose from your available popular topics and start practicing instantly."
          button="Choose Topic"
          onClick={() => nav("/topics")}
        />
      </div>

      <div className="section-head">
        <h2>My Learning Progress</h2>
        <span>Track your performance directly from the dashboard.</span>
      </div>

      <div className="metrics">
        <Metric label="Quizzes Completed" value={rows.length} />
        <Metric label="Questions Attempted" value={rows.reduce((sum, r) => sum + (r.total || 0), 0)} />
        <Metric label="Average Score" value={`${average}%`} />
      </div>

      <ProgressChart rows={recent} />

      <div className="section-head">
        <h2>Why QuizMate AI?</h2>
        <span>Simple for students. Smart enough for serious practice.</span>
      </div>

      <div className="grid-4">
        {[
          "AI-generated quizzes",
          "Multiple difficulty levels",
          "Upload your own notes",
          "Progress insights",
        ].map((x, i) => {
          const icons = [Sparkles, Target, Upload, BarChart3];
          const Icon = icons[i];
          return (
            <div className="info-card" key={x}>
              <div className="icon-box"><Icon size={20} /></div>
              <b>{x}</b>
              <p>Designed to keep learning fast and focused.</p>
            </div>
          );
        })}
      </div>
    </>
  );
}

/* =========================================================
   DASHBOARD PROGRESS GRAPH
========================================================= */

function ProgressChart({ rows }: { rows: any[] }) {
  const width = 640;
  const height = 240;
  const padX = 45;
  const padY = 30;
  const chartW = width - padX * 2;
  const chartH = height - padY * 2;

  const points = rows.map((r, i) => {
    const pct = Math.max(0, Math.min(100, ((r.score || 0) / Math.max(r.total || 1, 1)) * 100));
    const x = rows.length === 1 ? width / 2 : padX + (i * chartW) / (rows.length - 1);
    const y = padY + chartH - (pct / 100) * chartH;
    return { x, y, pct, label: r.topic || `Quiz ${i + 1}` };
  });

  const path = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <div className="history-card progress-chart-card">
      <div className="section-head">
        <div>
          <h2>Performance Trend</h2>
          <span>Latest quiz scores</span>
        </div>
        <BarChart3 size={20} />
      </div>

      {rows.length === 0 ? (
        <div className="empty">Complete a quiz to see your performance graph here.</div>
      ) : (
        <div style={{ width: "100%", overflowX: "auto" }}>
          <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label="Student quiz performance graph">
            {[0, 25, 50, 75, 100].map((v) => {
              const y = padY + chartH - (v / 100) * chartH;
              return (
                <g key={v}>
                  <line x1={padX} y1={y} x2={width - padX} y2={y} stroke="currentColor" opacity="0.12" />
                  <text x="8" y={y + 4} fontSize="11" fill="currentColor" opacity="0.65">{v}%</text>
                </g>
              );
            })}

            {path && (
              <path d={path} fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" opacity="0.85" />
            )}

            {points.map((p, i) => (
              <g key={`${p.label}-${i}`}>
                <circle cx={p.x} cy={p.y} r="6" fill="currentColor" />
                <text x={p.x} y={p.y - 12} textAnchor="middle" fontSize="11" fill="currentColor">{Math.round(p.pct)}%</text>
                <text x={p.x} y={height - 8} textAnchor="middle" fontSize="9" fill="currentColor" opacity="0.65">{String(i + 1)}</text>
              </g>
            ))}
          </svg>
        </div>
      )}
    </div>
  );
}

/* =========================================================
   ACTION CARD
========================================================= */

function ActionCard({
  icon,
  title,
  text,
  button,
  onClick,
}: {
  icon: React.ReactNode;
  title: string;
  text: string;
  button: string;
  onClick: () => void;
}) {
  return (
    <div className="action-card">
      <div className="icon-box">
        {icon}
      </div>

      <h3>{title}</h3>

      <p>{text}</p>

      <button
        className="primary"
        onClick={onClick}
      >
        {button}
        <ChevronRight size={17} />
      </button>
    </div>
  );
}

/* =========================================================
   POPULAR TOPICS
========================================================= */

function Topics({
  onStart,
}: {
  onStart: (
    text: string,
    name: string
  ) => void;
}) {
  const [topics, setTopics] = useState<
    { name: string; description: string }[]
  >([]);

  const [search, setSearch] = useState("");

  useEffect(() => {
    api
      .get("/api/topics")
      .then((r) => setTopics(r.data))
      .catch(() => setTopics([]));
  }, []);

  const filtered = useMemo(
    () =>
      topics.filter((t) =>
        t.name
          .toLowerCase()
          .includes(search.toLowerCase())
      ),
    [topics, search]
  );

  return (
    <>
      <PageTitle
        title="Popular Topics"
        subtitle="Pick a topic. No upload needed."
      />

      <input
        className="search"
        value={search}
        onChange={(e) =>
          setSearch(e.target.value)
        }
        placeholder="🔎 Search topics..."
      />

      <div className="topic-grid">
        {filtered.map((t) => (
          <div
            className="topic-card"
            key={t.name}
          >
            <div className="topic-icon">
              <Brain size={22} />
            </div>

            <div>
              <h3>{t.name}</h3>
              <p>{t.description}</p>
            </div>

            <button
              className="secondary"
              onClick={async () => {
                try {
                  const r = await api.get(
                    `/api/topics/${encodeURIComponent(
                      t.name
                    )}`
                  );

                  onStart(
                    r.data.text,
                    t.name
                  );
                } catch {
                  alert(
                    "Could not load this topic."
                  );
                }
              }}
            >
              Practice
              <ChevronRight size={16} />
            </button>
          </div>
        ))}
      </div>
    </>
  );
}

/* =========================================================
   GENERATE FROM TOPIC
========================================================= */

function TopicGenerator({
  onStart,
}: {
  onStart: (topic: string) => void;
}) {
  const [topic, setTopic] = useState("");
  const [error, setError] = useState("");

  const submit = () => {
    const value = topic.trim();

    if (value.length < 2) {
      setError("Please enter a topic.");
      return;
    }

    setError("");
    onStart(value);
  };

  return (
    <>
      <PageTitle
        title="✨ Generate a Quiz from Any Topic"
        subtitle="Enter any subject or concept. QuizMate AI will create a fresh quiz for you."
      />

      <div className="config-card">
        <div className="source-pill">
          💡 AI Topic Generator
        </div>

        <h2>What do you want to learn?</h2>

        <p className="muted">
          Try topics like Machine Learning, Python, IoT,
          Data Structures, Cloud Computing, or any subject you know.
        </p>

        <label>
          Topic
          <input
            className="search"
            value={topic}
            onChange={(e) => {
              setTopic(e.target.value);
              if (error) setError("");
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") submit();
            }}
            placeholder="e.g. Machine Learning"
            autoFocus
          />
        </label>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <button
          className="primary big"
          disabled={!topic.trim()}
          onClick={submit}
        >
          <Sparkles size={18} />
          Continue to Quiz Settings
        </button>
      </div>
    </>
  );
}

/* =========================================================
   QUIZ CONFIGURATION
========================================================= */

function QuizConfig({
  sourceText,
  sourceName,
  topic,
  onQuiz,
}: {
  sourceText?: string;
  sourceName: string;
  topic?: string;
  onQuiz: (
    q: Question[],
    name: string,
    diff: string,
    durationMinutes: number
  ) => void;
}) {
  const [count, setCount] = useState(10);
  const [type, setType] = useState("MCQ");
  const [difficulty, setDifficulty] =
    useState("Medium");
  const [durationMinutes, setDurationMinutes] =
    useState(0); // 0 = no time limit

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const generate = async () => {
    try {
      setLoading(true);
      setError("");

      const payload: Record<string, any> = {
        count,
        question_type: type,
        difficulty,
      };

      if (topic) {
        payload.topic = topic;
        payload.source_name = topic;
      } else {
        payload.source_text = sourceText;
        payload.source_name = sourceName;
      }

      const r = await api.post(
        "/api/quiz/generate",
        payload
      );

      onQuiz(
        r.data.questions,
        sourceName,
        difficulty,
        durationMinutes
      );
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
          "Quiz generation failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="config-card">
      <div className="source-pill">
        📚 {sourceName}
      </div>

      <h2>Create Your Quiz</h2>

      <p className="muted">
        Choose settings that feel right for you.
      </p>

      <div className="form-grid">
        <Select
          label="Number of questions"
          value={String(count)}
          set={(v) => setCount(Number(v))}
          options={["5", "10", "15", "20"]}
        />

        <Select
          label="Question type"
          value={type}
          set={setType}
          options={[
            "MCQ",
            "True / False",
            "Short Answer",
            "Mixed",
          ]}
        />

        <Select
          label="Difficulty"
          value={difficulty}
          set={setDifficulty}
          options={[
            "Easy",
            "Medium",
            "Hard",
            "Mixed",
          ]}
        />

        <Select
          label="Test duration"
          value={durationMinutes === 0 ? "No limit" : String(durationMinutes)}
          set={(v) => setDurationMinutes(v === "No limit" ? 0 : Number(v))}
          options={[
            "No limit",
            "5",
            "10",
            "15",
            "20",
            "30",
            "45",
            "60",
          ]}
        />
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      <button
        className="primary big"
        disabled={loading}
        onClick={generate}
      >
        {loading ? (
          <>
            <span className="spinner" />
            Creating your quiz...
          </>
        ) : (
          <>
            <Sparkles size={18} />
            Generate My Quiz
          </>
        )}
      </button>
    </div>
  );
}

/* =========================================================
   SELECT
========================================================= */

function Select({
  label,
  value,
  set,
  options,
}: {
  label: string;
  value: string;
  set: (v: string) => void;
  options: string[];
}) {
  return (
    <label>
      {label}

      <select
        value={value}
        onChange={(e) =>
          set(e.target.value)
        }
      >
        {options.map((o) => (
          <option key={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

/* =========================================================
   QUIZ
========================================================= */

function Quiz({
  questions,
  sourceName,
  difficulty,
  durationMinutes,
  onDone,
}: {
  questions: Question[];
  sourceName: string;
  difficulty: string;
  durationMinutes: number;
  onDone: (
    result: any,
    answers: Record<string, string>
  ) => void;
}) {
  const [answers, setAnswers] =
    useState<Record<string, string>>({});

  const [index, setIndex] = useState(0);
  const [timeLeft, setTimeLeft] = useState(
    durationMinutes > 0 ? durationMinutes * 60 : 0
  );
  const [submitting, setSubmitting] = useState(false);
  const answersRef = useRef<Record<string, string>>({});
  const submittedRef = useRef(false);

  const q = questions[index];

  const answer = (v: string) => {
    setAnswers((a) => {
      const next = {
        ...a,
        [String(index)]: v,
      };
      answersRef.current = next;
      return next;
    });
  };

  if (!q) {
    return (
      <div className="error">
        No questions available.
      </div>
    );
  }

  const submit = async (autoSubmit = false) => {
    if (submittedRef.current || submitting) return;

    submittedRef.current = true;
    setSubmitting(true);

    const finalAnswers = answersRef.current;

    try {
      const r = await api.post(
        "/api/quiz/submit",
        {
          source_name: sourceName,
          difficulty,
          questions,
          answers: finalAnswers,
        }
      );

      onDone(r.data, finalAnswers);
    } catch (e: any) {
      submittedRef.current = false;
      setSubmitting(false);
      alert(
        e?.response?.data?.detail ||
          (autoSubmit
            ? "Time expired, but the quiz could not be submitted. Please try again."
            : "Could not submit quiz.")
      );
    }
  };

  useEffect(() => {
    if (durationMinutes <= 0 || submittedRef.current) return;

    if (timeLeft <= 0) {
      submit(true);
      return;
    }

    const timer = window.setInterval(() => {
      setTimeLeft((current) => {
        if (current <= 1) {
          window.clearInterval(timer);
          return 0;
        }
        return current - 1;
      });
    }, 1000);

    return () => window.clearInterval(timer);
  }, [durationMinutes, timeLeft]);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  };

  const progress =
    ((index + 1) / questions.length) * 100;

  return (
    <div className="quiz-page">
      <div className="quiz-top">
        <span>
          Question {index + 1} of{" "}
          {questions.length}
        </span>

        <span>
          {durationMinutes > 0 ? (
            <>
              ⏱ {formatTime(timeLeft)} &nbsp;•&nbsp; {Math.round(progress)}%
            </>
          ) : (
            <>{Math.round(progress)}%</>
          )}
        </span>
      </div>

      {durationMinutes > 0 && timeLeft <= 60 && timeLeft > 0 && (
        <div className="error" style={{ marginBottom: 12 }}>
          ⏰ Less than one minute remaining. Your quiz will be submitted automatically when the timer reaches 00:00.
        </div>
      )}

      <div className="progress">
        <div
          style={{
            width: `${progress}%`,
          }}
        />
      </div>

      <div className="question-card">
        <div className="tag">
          {q.type}
        </div>

        <h2>{q.question}</h2>

        {q.type === "MCQ" && (
          <div className="options">
            {(q.options || []).map(
              (o, i) => (
                <button
                  key={o}
                  onClick={() =>
                    answer(o)
                  }
                  className={
                    answers[index] === o
                      ? "option selected"
                      : "option"
                  }
                >
                  <span>
                    {String.fromCharCode(
                      65 + i
                    )}
                  </span>

                  {o}
                </button>
              )
            )}
          </div>
        )}

        {q.type === "True / False" && (
          <div className="options two">
            {["True", "False"].map(
              (o) => (
                <button
                  key={o}
                  onClick={() =>
                    answer(o)
                  }
                  className={
                    answers[index] === o
                      ? "option selected"
                      : "option"
                  }
                >
                  <span>
                    {o === "True"
                      ? "✓"
                      : "✕"}
                  </span>

                  {o}
                </button>
              )
            )}
          </div>
        )}

        {q.type === "Short Answer" && (
          <textarea
            className="answer-box"
            value={
              answers[index] || ""
            }
            onChange={(e) =>
              answer(e.target.value)
            }
            placeholder="Write your answer..."
          />
        )}

        <div className="quiz-actions">
          {index > 0 && (
            <button
              className="secondary"
              onClick={() =>
                setIndex(index - 1)
              }
            >
              Back
            </button>
          )}

          {index <
          questions.length - 1 ? (
            <button
              className="primary"
              disabled={submitting}
              onClick={() =>
                setIndex(index + 1)
              }
            >
              Next
              <ChevronRight size={17} />
            </button>
          ) : (
            <button
              className="primary"
              disabled={submitting}
              onClick={() => submit(false)}
            >
              Submit Quiz
              <CheckCircle2 size={17} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   RESULTS
========================================================= */

function Results({
  result,
  questions,
  answers,
}: {
  result: any;
  questions: Question[];
  answers: Record<string, string>;
}) {
  const normalize = (v: string) => String(v || "").trim().toLowerCase();

  const isCorrect = (q: Question, userAnswer: string) => {
    const user = normalize(userAnswer);
    const correct = normalize(q.answer);
    if (!user) return false;
    if (q.type === "MCQ" || q.type === "True / False") return user === correct;
    const keywords = Array.isArray((q as any).keywords) ? (q as any).keywords : [];
    if (keywords.length) return keywords.some((k: string) => user.includes(normalize(k)));
    return user === correct;
  };

  return (
    <>
      <PageTitle title="🎉 Quiz Complete!" subtitle="Here is your performance review." />

      <div className="result-hero">
        <div className="score-ring">
          <b>{result.percentage}%</b>
          <span>{result.score}/{result.total}</span>
        </div>
        <div>
          <h2>{result.percentage >= 80 ? "Excellent work!" : result.percentage >= 60 ? "Good progress!" : "Keep practicing!"}</h2>
          <p>You completed the quiz successfully.</p>
        </div>
      </div>

      <div className="review-legend" style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
        <span><b style={{ color: "#d93025" }}>● Wrong</b></span>
        <span><b style={{ color: "#2563eb" }}>● Skipped</b></span>
        <span><b style={{ color: "#15803d" }}>● Correct</b></span>
      </div>

      <div className="review-list">
        {questions.map((q, i) => {
          const userAnswer = answers[i] || "";
          const skipped = !userAnswer.trim();
          const correct = !skipped && isCorrect(q, userAnswer);
          const statusClass = skipped ? "review skipped" : correct ? "review correct" : "review wrong";

          return (
            <div className={statusClass} key={i} style={{ borderLeft: skipped ? "5px solid #2563eb" : correct ? "5px solid #15803d" : "5px solid #d93025" }}>
              <div>
                <b>{i + 1}. {q.question}</b>
                <p>
                  Your answer: <span>{userAnswer || "Skipped"}</span>
                  {skipped ? " — SKIPPED" : correct ? " — CORRECT" : " — WRONG"}
                </p>
                <p>Correct answer: <strong>{q.answer}</strong></p>
                <small>{q.explanation}</small>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

/* =========================================================
   UPLOAD NOTES (PDF / DOCX)
   IMPORTANT:
   Renamed from Upload -> UploadPDF
   to avoid conflict with lucide-react Upload icon.
========================================================= */

function UploadPDF({
  onStart,
}: {
  onStart: (
    text: string,
    name: string
  ) => void;
}) {
  const [file, setFile] =
    useState<File | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const upload = async () => {
    if (!file) return;

    try {
      setLoading(true);
      setError("");

      const fd = new FormData();

      fd.append("file", file);

      const r = await api.post(
        "/api/pdf/extract",
        fd,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      onStart(
        r.data.text,
        r.data.filename
      );
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
          "Could not read this document."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageTitle
        title="📄 Turn Your Notes Into a Quiz"
        subtitle="Upload a PDF or DOCX and create questions from it."
      />

      <div className="upload-card">
        <div className="upload-icon">
          <Upload size={30} />
        </div>

        <h2>
          {file
            ? file.name
            : "Drop your PDF or DOCX here"}
        </h2>

        <p>
          PDF or DOCX • Up to 10 MB •
          Text-based PDFs and DOCX files work best
        </p>

        <label className="file-btn">
          Choose PDF

          <input
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={(e) =>
              setFile(
                e.target.files?.[0] ||
                  null
              )
            }
          />
        </label>

        {file && (
          <button
            className="primary big"
            disabled={loading}
            onClick={upload}
          >
            {loading
              ? "Reading document..."
              : "Continue to Quiz Settings"}
          </button>
        )}

        {error && (
          <div className="error">
            {error}
          </div>
        )}
      </div>
    </>
  );
}

/* =========================================================
   YOUTUBE QUIZ GENERATOR
========================================================= */

function YouTubeGenerator({
  onStart,
}: {
  onStart: (text: string, name: string) => void;
}) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async () => {
    const value = url.trim();

    if (!value) {
      setError("Please paste a YouTube video URL.");
      return;
    }

    if (
      !/^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/|youtube\.com\/embed\/|youtube\.com\/live\/)/i.test(value)
    ) {
      setError("Please enter a valid YouTube video URL.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const r = await api.post("/api/youtube/extract", {
        url: value,
      });

      onStart(
        r.data.text,
        r.data.title || "YouTube Video"
      );
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
          "Could not read the YouTube transcript. Make sure captions/transcript are available."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageTitle
        title="🎥 Generate a Quiz from YouTube"
        subtitle="Paste a YouTube video link and QuizMate AI will use its transcript to create a quiz."
      />

      <div className="config-card">
        <div className="source-pill">
          🎥 YouTube Quiz Generator
        </div>

        <h2>Paste your YouTube video</h2>

        <p className="muted">
          Use an educational video with available captions or a transcript.
          QuizMate will extract the transcript and continue to the normal quiz settings.
        </p>

        <label>
          YouTube URL
          <input
            className="search"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              if (error) setError("");
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") submit();
            }}
            placeholder="https://www.youtube.com/watch?v=..."
            autoFocus
          />
        </label>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <button
          className="primary big"
          disabled={!url.trim() || loading}
          onClick={submit}
        >
          {loading ? (
            <>
              <span className="spinner" />
              Reading YouTube transcript...
            </>
          ) : (
            <>
              <Youtube size={18} />
              Continue to Quiz Settings
            </>
          )}
        </button>
      </div>
    </>
  );
}

/* =========================================================
   GENERATE FROM GIVEN INFORMATION
========================================================= */

function InformationGenerator({
  onStart,
}: {
  onStart: (text: string, name: string) => void;
}) {
  const [text, setText] = useState("");
  const [name, setName] = useState("My Information");
  const [error, setError] = useState("");

  const submit = () => {
    const value = text.trim();
    if (value.length < 20) {
      setError("Please enter at least 20 characters of information.");
      return;
    }
    setError("");
    onStart(value, name.trim() || "My Information");
  };

  return (
    <>
      <PageTitle
        title="📝 Generate Quiz from Given Information"
        subtitle="Paste any study information, notes, article text, or content and let AI create a quiz."
      />

      <div className="config-card">
        <div className="source-pill">🧠 Information Quiz Generator</div>

        <label>
          Information title
          <input
            className="search"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Operating Systems Notes"
          />
        </label>

        <label>
          Enter your information
          <textarea
            className="answer-box"
            style={{ minHeight: 220 }}
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              if (error) setError("");
            }}
            placeholder="Paste your study material here..."
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button className="primary big" disabled={text.trim().length < 20} onClick={submit}>
          <Sparkles size={18} />
          Continue to Quiz Settings
        </button>
      </div>
    </>
  );
}

/* =========================================================
   SUMMARIZER
========================================================= */

function Summarize() {
  const [file, setFile] =
    useState<File | null>(null);

  const [mode, setMode] =
    useState("Exam Revision Notes");

  const [summary, setSummary] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const run = async () => {
    if (!file) return;

    try {
      setLoading(true);
      setError("");

      const fd = new FormData();

      fd.append("file", file);

      const ext = await api.post(
        "/api/pdf/extract",
        fd,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      const r = await api.post(
        "/api/summary",
        {
          text: ext.data.text,
          mode,
        }
      );

      setSummary(r.data.summary);
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ||
          "Summary failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageTitle
        title="📝 AI Notes Summarizer"
        subtitle="Turn long PDF or DOCX notes into clear revision material."
      />

      <div className="config-card">
        <input
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={(e) =>
            setFile(
              e.target.files?.[0] ||
                null
            )
          }
        />

        <Select
          label="Summary style"
          value={mode}
          set={setMode}
          options={[
            "Quick Summary",
            "Detailed Summary",
            "Exam Revision Notes",
            "Explain Simply",
          ]}
        />

        <button
          className="primary big"
          disabled={!file || loading}
          onClick={run}
        >
          {loading
            ? "Creating summary..."
            : "✨ Summarize Notes"}
        </button>

        {error && (
          <div className="error">
            {error}
          </div>
        )}
      </div>

      {summary && (
        <article className="summary-card">
          <div className="markdownish">
            {summary
              .split("\n")
              .map((line, i) => (
                <p key={i}>
                  {line}
                </p>
              ))}
          </div>
        </article>
      )}
    </>
  );
}

/* =========================================================
   PROGRESS
========================================================= */

function Progress() {
  const [rows, setRows] =
    useState<any[]>([]);

  useEffect(() => {
    api
      .get("/api/results")
      .then((r) => setRows(r.data))
      .catch(() => setRows([]));
  }, []);

  const avg = rows.length
    ? Math.round(
        rows.reduce(
          (s, r) =>
            s +
            (r.score / r.total) *
              100,
          0
        ) / rows.length
      )
    : 0;

  return (
    <>
      <PageTitle
        title="📊 My Progress"
        subtitle="See how your practice is going."
      />

      <div className="metrics">
        <Metric
          label="Quizzes"
          value={rows.length}
        />

        <Metric
          label="Questions"
          value={rows.reduce(
            (s, r) =>
              s + r.total,
            0
          )}
        />

        <Metric
          label="Average Score"
          value={`${avg}%`}
        />
      </div>

      <div className="history-card">
        <div className="section-head">
          <h2>Recent quizzes</h2>
          <History size={20} />
        </div>

        {rows.length === 0 ? (
          <div className="empty">
            Complete your first quiz
            to see progress here.
          </div>
        ) : (
          rows.map((r, i) => (
            <div
              className="history-row"
              key={i}
            >
              <div>
                <b>{r.topic}</b>

                <span>
                  {new Date(
                    r.created_at
                  ).toLocaleString()}
                </span>
              </div>

              <strong>
                {r.score}/{r.total}
              </strong>

              <span>
                {r.difficulty}
              </span>
            </div>
          ))
        )}
      </div>
    </>
  );
}

/* =========================================================
   SMALL COMPONENTS
========================================================= */

function Metric({
  label,
  value,
}: {
  label: string;
  value: any;
}) {
  return (
    <div className="metric">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function PageTitle({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <div className="page-title">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
  );
}

/* =========================================================
   MAIN APP
========================================================= */

export default function App() {
  const [token, setTok] =
    useState<string | null>(
      localStorage.getItem(
        "qm_token"
      )
    );

  const [user, setUser] =
    useState<User | null>(
      JSON.parse(
        localStorage.getItem(
          "qm_user"
        ) || "null"
      )
    );

  const [source, setSource] =
    useState<{
      text: string;
      name: string;
      topic?: string;
      kind:
        | "popular-topic"
        | "document"
        | "direct-topic"
        | "youtube"
        | "information";
    } | null>(null);

  const [quiz, setQuiz] =
    useState<Question[] | null>(
      null
    );

  const [quizMeta, setQuizMeta] =
    useState({
      name: "",
      difficulty: "Medium",
      durationMinutes: 0,
    });

  const [result, setResult] =
    useState<any | null>(null);

  const [answers, setAnswers] =
    useState<
      Record<string, string>
    >({});

  const nav = useNavigate();

  useEffect(() => {
    setToken(token);
  }, [token]);

  const login = (
    t: string,
    u: User
  ) => {
    localStorage.setItem(
      "qm_token",
      t
    );

    localStorage.setItem(
      "qm_user",
      JSON.stringify(u)
    );

    setTok(t);
    setUser(u);
  };

  const logout = () => {
    localStorage.removeItem(
      "qm_token"
    );

    localStorage.removeItem(
      "qm_user"
    );

    setToken(null);

    setTok(null);
    setUser(null);
    setSource(null);
    setQuiz(null);
    setResult(null);
    setAnswers({});
  };

  if (!user) {
    return (
      <Auth onLogin={login} />
    );
  }

  const guarded = (
    element: React.ReactNode
  ) => (
    <Layout
      user={user}
      logout={logout}
    >
      {element}
    </Layout>
  );

  /* Start quiz source */
  const startQuiz = (
    text: string,
    name: string
  ) => {
    setSource({
      text,
      name,
      kind: "popular-topic",
    });

    setQuiz(null);
    setResult(null);
    setAnswers({});
  };

  /* Start uploaded document quiz */
  const startDocumentQuiz = (
    text: string,
    name: string
  ) => {
    setSource({
      text,
      name,
      kind: "document",
    });

    setQuiz(null);
    setResult(null);
    setAnswers({});
  };

  /* Start direct AI topic quiz */
  const startTopicQuiz = (topic: string) => {
    setSource({
      text: "",
      name: topic,
      topic,
      kind: "direct-topic",
    });

    setQuiz(null);
    setResult(null);
    setAnswers({});
    nav("/generate-topic");
  };

  /* Start quiz from user-provided information */
  const startInformationQuiz = (
    text: string,
    name: string
  ) => {
    setSource({
      text,
      name,
      kind: "information",
    });
    setQuiz(null);
    setResult(null);
    setAnswers({});
    nav("/generate-information");
  };

  /* Start YouTube transcript quiz */
  const startYouTubeQuiz = (
    text: string,
    name: string
  ) => {
    setSource({
      text,
      name,
      kind: "youtube",
    });

    setQuiz(null);
    setResult(null);
    setAnswers({});
    nav("/youtube");
  };

  /* Quiz generated successfully */
  const handleQuizGenerated = (
    q: Question[],
    name: string,
    difficulty: string,
    durationMinutes: number
  ) => {
    setQuiz(q);

    setQuizMeta({
      name,
      difficulty,
      durationMinutes,
    });

    setResult(null);
    setAnswers({});

    nav("/quiz");
  };

  return (
    <Routes>
      {/* HOME */}
      <Route
        path="/"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />

      {/* DASHBOARD */}
      <Route
        path="/dashboard"
        element={guarded(
          <Dashboard user={user} />
        )}
      />

      {/* GENERATE FROM TOPIC */}
      <Route
        path="/generate-topic"
        element={guarded(
          source?.kind === "direct-topic" && source.topic ? (
            <QuizConfig
              sourceName={source.name}
              topic={source.topic}
              onQuiz={
                handleQuizGenerated
              }
            />
          ) : (
            <TopicGenerator
              onStart={startTopicQuiz}
            />
          )
        )}
      />

      {/* TOPICS */}
      <Route
        path="/topics"
        element={guarded(
          source?.kind === "popular-topic" ? (
            <QuizConfig
              sourceText={source.text}
              sourceName={source.name}
              onQuiz={
                handleQuizGenerated
              }
            />
          ) : (
            <Topics
              onStart={startQuiz}
            />
          )
        )}
      />

      {/* UPLOAD PDF */}
      <Route
        path="/upload"
        element={guarded(
          source?.kind === "document" ? (
            <QuizConfig
              sourceText={source.text}
              sourceName={source.name}
              onQuiz={
                handleQuizGenerated
              }
            />
          ) : (
            <UploadPDF
              onStart={startDocumentQuiz}
            />
          )
        )}
      />

      {/* YOUTUBE QUIZ */}
      <Route
        path="/youtube"
        element={guarded(
          source?.kind === "youtube" ? (
            <QuizConfig
              sourceText={source.text}
              sourceName={source.name}
              onQuiz={handleQuizGenerated}
            />
          ) : (
            <YouTubeGenerator
              onStart={startYouTubeQuiz}
            />
          )
        )}
      />

      {/* GENERATE FROM INFORMATION */}
      <Route
        path="/generate-information"
        element={guarded(
          source?.kind === "information" ? (
            <QuizConfig
              sourceText={source.text}
              sourceName={source.name}
              onQuiz={handleQuizGenerated}
            />
          ) : (
            <InformationGenerator
              onStart={startInformationQuiz}
            />
          )
        )}
      />

      {/* SUMMARIZER */}
      <Route
        path="/summarize"
        element={guarded(
          <Summarize />
        )}
      />

      {/* PROGRESS */}
      <Route
        path="/progress"
        element={guarded(
          <Progress />
        )}
      />

      {/* QUIZ */}
      <Route
  path="/quiz"
  element={guarded(
    quiz && !result ? (
      <Quiz
        questions={quiz}
        sourceName={
          quizMeta.name
        }
        difficulty={
          quizMeta.difficulty
        }
        durationMinutes={
          quizMeta.durationMinutes
        }
        onDone={(
          r,
          a
        ) => {
          setResult(r);
          setAnswers(a);
        }}
      />
    ) : result ? (
      <>
        <Results
          result={result}
          questions={quiz || []}
          answers={answers}
        />

        <Feedback />
      </>
    ) : (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  )}
/>
    </Routes>
  );
}
import { useEffect, useMemo, useState } from "react";
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
} from "lucide-react";

import api, { setToken } from "./api";
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
    ["/upload", "Upload PDF", Upload],
    ["/summarize", "Summarize", FileText],
    ["/progress", "My Progress", BarChart3],
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

  return (
    <>
      <div className="hero">
        <div>
          <div className="eyebrow">
            YOUR PERSONAL AI STUDY SPACE
          </div>

          <h1>
            Hello, {user.name}! 👋
          </h1>

          <p>
            What would you like to learn today?
          </p>
        </div>

        <div className="hero-art">
          <Sparkles size={34} />
        </div>
      </div>

      <div className="grid-3">
        <ActionCard
          icon={<Target />}
          title="Start a Quiz"
          text="Choose a popular topic and test your knowledge."
          button="Practice a Topic"
          onClick={() => nav("/topics")}
        />

        <ActionCard
          icon={<Upload />}
          title="Upload Notes"
          text="Turn your PDF notes into a personalized quiz."
          button="Upload PDF"
          onClick={() => nav("/upload")}
        />

        <ActionCard
          icon={<FileText />}
          title="Summarize PDF"
          text="Turn long study material into quick revision notes."
          button="Summarize"
          onClick={() => nav("/summarize")}
        />
      </div>

      <div className="section-head">
        <h2>Why QuizMate AI?</h2>

        <span>
          Simple for students. Smart enough for serious practice.
        </span>
      </div>

      <div className="grid-4">
        {[
          "AI-generated quizzes",
          "Multiple difficulty levels",
          "Upload your own notes",
          "Progress insights",
        ].map((x, i) => {
          const icons = [
            Sparkles,
            Target,
            Upload,
            BarChart3,
          ];

          const Icon = icons[i];

          return (
            <div
              className="info-card"
              key={x}
            >
              <div className="icon-box">
                <Icon size={20} />
              </div>

              <b>{x}</b>

              <p>
                Designed to keep learning fast
                and focused.
              </p>
            </div>
          );
        })}
      </div>
    </>
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
   QUIZ CONFIGURATION
========================================================= */

function QuizConfig({
  sourceText,
  sourceName,
  onQuiz,
}: {
  sourceText: string;
  sourceName: string;
  onQuiz: (
    q: Question[],
    name: string,
    diff: string
  ) => void;
}) {
  const [count, setCount] = useState(10);
  const [type, setType] = useState("MCQ");
  const [difficulty, setDifficulty] =
    useState("Medium");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const generate = async () => {
    try {
      setLoading(true);
      setError("");

      const r = await api.post(
        "/api/quiz/generate",
        {
          source_text: sourceText,
          source_name: sourceName,
          count,
          question_type: type,
          difficulty,
        }
      );

      onQuiz(
        r.data.questions,
        sourceName,
        difficulty
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
  onDone,
}: {
  questions: Question[];
  sourceName: string;
  difficulty: string;
  onDone: (
    result: any,
    answers: Record<string, string>
  ) => void;
}) {
  const [answers, setAnswers] =
    useState<Record<string, string>>({});

  const [index, setIndex] = useState(0);

  const q = questions[index];

  const answer = (v: string) => {
    setAnswers((a) => ({
      ...a,
      [String(index)]: v,
    }));
  };

  if (!q) {
    return (
      <div className="error">
        No questions available.
      </div>
    );
  }

  const submit = async () => {
    try {
      const r = await api.post(
        "/api/quiz/submit",
        {
          source_name: sourceName,
          difficulty,
          questions,
          answers,
        }
      );

      onDone(r.data, answers);
    } catch (e: any) {
      alert(
        e?.response?.data?.detail ||
          "Could not submit quiz."
      );
    }
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
          {Math.round(progress)}%
        </span>
      </div>

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
              onClick={submit}
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
  return (
    <>
      <PageTitle
        title="🎉 Quiz Complete!"
        subtitle="Here is your performance review."
      />

      <div className="result-hero">
        <div className="score-ring">
          <b>{result.percentage}%</b>

          <span>
            {result.score}/{result.total}
          </span>
        </div>

        <div>
          <h2>
            {result.percentage >= 80
              ? "Excellent work!"
              : result.percentage >= 60
              ? "Good progress!"
              : "Keep practicing!"}
          </h2>

          <p>
            You completed the quiz successfully.
          </p>
        </div>
      </div>

      <div className="review-list">
        {questions.map((q, i) => (
          <div
            className="review"
            key={i}
          >
            <div>
              <b>
                {i + 1}. {q.question}
              </b>

              <p>
                Your answer:{" "}
                <span>
                  {answers[i] ||
                    "Skipped"}
                </span>
              </p>

              <p>
                Correct answer:{" "}
                <strong>
                  {q.answer}
                </strong>
              </p>

              <small>
                {q.explanation}
              </small>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

/* =========================================================
   UPLOAD PDF
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
          "Could not read this PDF."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageTitle
        title="📄 Turn Your Notes Into a Quiz"
        subtitle="Upload a PDF and create questions from it."
      />

      <div className="upload-card">
        <div className="upload-icon">
          <Upload size={30} />
        </div>

        <h2>
          {file
            ? file.name
            : "Drop your PDF here"}
        </h2>

        <p>
          PDF only • Up to 10 MB •
          Text-based PDFs work best
        </p>

        <label className="file-btn">
          Choose PDF

          <input
            type="file"
            accept=".pdf,application/pdf"
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
              ? "Reading PDF..."
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
        title="📝 AI PDF Summarizer"
        subtitle="Turn long notes into clear revision material."
      />

      <div className="config-card">
        <input
          type="file"
          accept=".pdf,application/pdf"
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
            : "✨ Summarize PDF"}
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
    } | null>(null);

  const [quiz, setQuiz] =
    useState<Question[] | null>(
      null
    );

  const [quizMeta, setQuizMeta] =
    useState({
      name: "",
      difficulty: "Medium",
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
    });

    setQuiz(null);
    setResult(null);
    setAnswers({});
  };

  /* Quiz generated successfully */
  const handleQuizGenerated = (
    q: Question[],
    name: string,
    difficulty: string
  ) => {
    setQuiz(q);

    setQuizMeta({
      name,
      difficulty,
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

      {/* TOPICS */}
      <Route
        path="/topics"
        element={guarded(
          source ? (
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
          source ? (
            <QuizConfig
              sourceText={source.text}
              sourceName={source.name}
              onQuiz={
                handleQuizGenerated
              }
            />
          ) : (
            <UploadPDF
              onStart={startQuiz}
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
              onDone={(
                r,
                a
              ) => {
                setResult(r);
                setAnswers(a);
              }}
            />
          ) : result ? (
            <Results
              result={result}
              questions={quiz || []}
              answers={answers}
            />
          ) : (
            <Navigate
              to="/topics"
              replace
            />
          )
        )}
      />
    </Routes>
  );
}
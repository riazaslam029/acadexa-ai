import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useForm } from "react-hook-form";
import {
  Bell,
  BookOpen,
  Brain,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Search,
  Settings,
  Sun,
  Upload,
  User,
  X,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import {
  Link,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "./state/AuthContext";
import { DocumentProvider } from "./state/DocumentContext";
import {
  useArtifactsQuery,
  useChatHistoryQuery,
  useChatMutation,
  useDashboardQuery,
  useDocumentsQuery,
  useGenerateArtifactMutation,
  useLoginMutation,
  useRegisterMutation,
  useUploadDocumentMutation,
  normalizeApiError,
} from "./state/hooks";
import { ArtifactRenderer } from "./components/ArtifactRenderer";

type NavItem = { label: string; path: string; icon: JSX.Element };

const dashboardNav: NavItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: <LayoutDashboard size={18} /> },
  { label: "Upload", path: "/upload", icon: <Upload size={18} /> },
  { label: "Documents", path: "/documents", icon: <FileText size={18} /> },
  { label: "AI Chat", path: "/chat", icon: <Brain size={18} /> },
  { label: "Flashcards", path: "/flashcards", icon: <BookOpen size={18} /> },
  { label: "MCQs", path: "/mcqs", icon: <FileText size={18} /> },
  { label: "Quiz", path: "/quiz", icon: <Brain size={18} /> },
  { label: "Study Notes", path: "/study-notes", icon: <BookOpen size={18} /> },
  { label: "Profile", path: "/profile", icon: <User size={18} /> },
  { label: "Settings", path: "/settings", icon: <Settings size={18} /> },
];

function PublicLayout({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <main className="hero-grid min-h-screen text-[var(--text)]">
      <section className="mx-auto grid max-w-6xl gap-8 p-6 md:grid-cols-2 md:p-12">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <p className="caps mb-4">Acadexa AI</p>
          <h1 className="display text-4xl md:text-6xl">{title}</h1>
          <p className="mt-4 text-base text-[var(--muted)] md:text-lg">{subtitle}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="btn-primary" to="/dashboard">
              Open Dashboard
            </Link>
            <Link className="btn-ghost" to="/login">
              Login
            </Link>
          </div>
        </motion.div>

        <motion.div
          className="glass-panel p-6"
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h2 className="text-xl font-semibold">Built For Deep Study</h2>
          <ul className="mt-4 grid gap-3 text-sm text-[var(--muted)]">
            <li>Document-grounded chat with saved history</li>
            <li>Flashcards, MCQs, quizzes, notes, translations</li>
            <li>Roadmaps, study plans, and progress analytics</li>
          </ul>
          <nav className="mt-6 flex flex-wrap gap-2 text-sm">
            <Link className="tag" to="/login">
              Login
            </Link>
            <Link className="tag" to="/register">
              Register
            </Link>
          </nav>
        </motion.div>
      </section>
    </main>
  );
}

type AuthFormValues = {
  name: string;
  email: string;
  password: string;
};

function AuthPage({ title, mode }: { title: string; mode: "login" | "register" }) {
  const navigate = useNavigate();
  const { login } = useAuth();
  const loginMutation = useLoginMutation();
  const registerMutation = useRegisterMutation();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AuthFormValues>({
    defaultValues: {
      name: "",
      email: "",
      password: "",
    },
  });

  const isLoading = loginMutation.isPending || registerMutation.isPending;
  const errorText =
    normalizeApiError(loginMutation.error) !== "Something went wrong."
      ? normalizeApiError(loginMutation.error)
      : normalizeApiError(registerMutation.error);

  async function onSubmit(values: AuthFormValues) {
    if (mode === "register") {
      await registerMutation.mutateAsync({
        name: values.name,
        email: values.email,
        password: values.password,
      });
    }

    const tokenData = await loginMutation.mutateAsync({
      email: values.email,
      password: values.password,
    });
    login(tokenData.access_token);
    navigate("/dashboard");
  }

  return (
    <main className="hero-grid flex min-h-screen items-center justify-center p-6 text-[var(--text)]">
      <motion.section
        className="glass-panel w-full max-w-md p-8"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="display text-3xl">{title}</h1>
        {mode === "register" ? (
          <p className="mt-2 text-sm text-[var(--muted)]">Create your account to get started.</p>
        ) : (
          <p className="mt-2 text-sm text-[var(--muted)]">Welcome back! Sign in to continue.</p>
        )}
        <form className="mt-6 grid gap-3" onSubmit={handleSubmit(onSubmit)}>
          {mode === "register" && (
            <input
              className="input"
              placeholder="Full Name"
              aria-label="Full Name"
              {...register("name", { required: "Name is required" })}
            />
          )}
          {errors.name && <span className="text-sm text-red-500">{errors.name.message}</span>}

          <input
            className="input"
            placeholder="Email"
            aria-label="Email"
            type="email"
            {...register("email", { required: "Email is required" })}
          />
          {errors.email && <span className="text-sm text-red-500">{errors.email.message}</span>}

          <input
            className="input"
            placeholder="Password (min 8 characters)"
            aria-label="Password"
            type="password"
            {...register("password", { required: "Password is required", minLength: { value: 8, message: "Password must be at least 8 characters" } })}
          />
          {errors.password && <span className="text-sm text-red-500">{errors.password.message}</span>}

          <button className="btn-primary" disabled={isLoading} type="submit">
            {isLoading ? "Please wait..." : mode === "register" ? "Create Account" : "Sign In"}
          </button>
          {errorText !== "Something went wrong." && (
            <p className="text-sm text-red-500">{errorText}</p>
          )}
          <Link className="btn-ghost text-center" to="/">
            Back Home
          </Link>
        </form>
      </motion.section>
    </main>
  );
}

function ProtectedRoute() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

function DashboardLayout({
  isDark,
  setIsDark,
  children,
}: {
  isDark: boolean;
  setIsDark: (v: boolean) => void;
  children: React.ReactNode;
}) {
  const location = useLocation();
  const { logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const title = dashboardNav.find((item) => location.pathname.startsWith(item.path))?.label ?? "Dashboard";

  return (
    <div className={isDark ? "theme-dark" : "theme-light"}>
      <div className="dashboard-wrap min-h-screen text-[var(--text)]">
        <button
          className="icon-btn fixed left-4 top-4 z-50 md:hidden"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle menu"
        >
          {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
        </button>

        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <aside
          className={`glass-panel fixed z-40 m-3 flex h-[calc(100vh-1.5rem)] w-64 flex-col gap-2 p-4 transition-transform md:static md:translate-x-0 ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <p className="caps mb-2">Acadexa AI</p>
          {dashboardNav.map((item) => (
            <Link key={item.path} to={item.path} className="side-link" onClick={() => setSidebarOpen(false)}>
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
          <button className="side-link mt-auto" onClick={logout}>
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </aside>

        <div className="flex-1 p-3">
          <header className="glass-panel mb-3 flex items-center gap-3 p-4">
            <h1 className="display text-2xl">{title}</h1>
            <div className="ml-auto flex items-center gap-2">
              <button className="icon-btn" aria-label="Search">
                <Search size={18} />
              </button>
              <button className="icon-btn" aria-label="Notifications">
                <Bell size={18} />
              </button>
              <button
                className="icon-btn"
                aria-label="Toggle theme"
                onClick={() => setIsDark((v) => !v)}
              >
                {isDark ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          </header>

          <Outlet />
        </div>
      </div>
    </div>
  );
}

function DashboardCard({ title, description }: { title: string; description: string | number }) {
  return (
    <motion.article
      className="glass-panel p-5"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="mt-2 text-sm text-[var(--muted)]">{description}</p>
    </motion.article>
  );
}

function DashboardHome() {
  const { isAuthenticated } = useAuth();
  const dashboardQuery = useDashboardQuery(isAuthenticated);

  if (dashboardQuery.isLoading) {
    return (
      <section className="glass-panel p-6">
        <div className="grid gap-3">
          <div className="h-24 w-full animate-pulse rounded-lg bg-[var(--glass)]" />
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-20 w-full animate-pulse rounded-lg bg-[var(--glass)]" />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (dashboardQuery.error) {
    return (
      <section className="glass-panel p-6">
        <p className="text-red-500">{normalizeApiError(dashboardQuery.error)}</p>
      </section>
    );
  }

  const data = dashboardQuery.data;
  if (!data) {
    return <section className="glass-panel p-6">No dashboard data found.</section>;
  }

  return (
    <div className="grid gap-3">
      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <DashboardCard title="Total Documents" description={String(data.stats.total_documents)} />
        <DashboardCard title="AI Requests" description={String(data.stats.total_ai_requests)} />
        <DashboardCard title="Storage Used (bytes)" description={String(data.stats.storage_used_bytes)} />
      </section>
      <section className="glass-panel p-6">
        <h3 className="text-xl font-semibold">Recent Uploads</h3>
        <ul className="mt-3 grid gap-2 text-sm text-[var(--muted)]">
          {data.recent_uploads.map((item) => (
            <li key={item.id} className="flex justify-between">
              <span>{item.original_name}</span>
              <span className="text-xs">{item.processing_status}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function UploadPage() {
  const [progress, setProgress] = useState(0);
  const uploadMutation = useUploadDocumentMutation();
  const { register, handleSubmit, reset } = useForm<{ file: FileList }>();

  async function onSubmit(values: { file: FileList }) {
    const file = values.file?.[0];
    if (!file) return;

    setProgress(0);
    await uploadMutation.mutateAsync({ file, onProgress: setProgress });
    reset();
  }

  return (
    <section className="glass-panel p-6">
      <h2 className="display text-3xl">Upload Document</h2>
      <p className="mt-2 text-sm text-[var(--muted)]">
        Supported formats: PDF, DOCX, TXT, PNG, JPEG, JPG
      </p>
      <form className="mt-4 grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <input type="file" className="input" {...register("file")} />
        <div className="glass-panel h-3 overflow-hidden">
          <div className="h-full bg-emerald-500 transition-all" style={{ width: `${progress}%` }} />
        </div>
        <button type="submit" className="btn-primary" disabled={uploadMutation.isPending}>
          {uploadMutation.isPending ? "Uploading..." : "Upload File"}
        </button>
        {uploadMutation.error && (
          <p className="text-sm text-red-500">{normalizeApiError(uploadMutation.error)}</p>
        )}
      </form>
    </section>
  );
}

function ChatPage() {
  const { isAuthenticated } = useAuth();
  const documentsQuery = useDocumentsQuery(isAuthenticated);

  const [documentId, setDocumentId] = useState<number | null>(null);
  const { register, handleSubmit, reset } = useForm<{ question: string }>();
  const chatMutation = useChatMutation(documentId ?? 1);
  const historyQuery = useChatHistoryQuery(documentId ?? 1, documentId !== null);

  async function onSubmit(values: { question: string }) {
    if (!documentId) return;
    await chatMutation.mutateAsync(values.question);
    await historyQuery.refetch();
    reset();
  }

  const selectedDoc = documentsQuery.data?.find((d) => d.id === documentId);

  return (
    <section className="glass-panel p-6">
      <h2 className="display text-3xl">AI Chat</h2>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div>
          <label className="text-sm text-[var(--muted)]">Select Document</label>
          <select
            className="input mt-1"
            value={documentId ?? ""}
            onChange={(e) => setDocumentId(Number(e.target.value))}
          >
            <option value="">Choose a document...</option>
            {documentsQuery.data?.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.original_name}
              </option>
            ))}
          </select>
        </div>

        <div className="glass-panel p-3 text-sm text-[var(--muted)]">
          <strong>Selected:</strong>{" "}
          {selectedDoc ? `${selectedDoc.original_name} (${selectedDoc.processing_status})` : "None"}
        </div>
      </div>

      <form className="mt-4 flex gap-3" onSubmit={handleSubmit(onSubmit)}>
        <input
          className="input flex-1"
          placeholder="Ask from your document"
          {...register("question")}
          disabled={!documentId}
        />
        <button
          className="btn-primary"
          type="submit"
          disabled={chatMutation.isPending || !documentId}
        >
          {chatMutation.isPending ? "Thinking..." : "Send"}
        </button>
      </form>

      <div className="mt-5 grid gap-3">
        {historyQuery.data?.map((item) => (
          <div key={item.id} className="glass-panel p-4">
            <p className="text-sm font-semibold">Q: {item.question}</p>
            <div className="prose prose-sm mt-2 max-w-none text-[var(--text)]">
              <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                {item.answer}
              </ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ArtifactPage({
  title,
  artifactPath,
}: {
  title: string;
  artifactPath: string;
}) {
  const { isAuthenticated } = useAuth();
  const documentsQuery = useDocumentsQuery(isAuthenticated);

  const [documentId, setDocumentId] = useState<number | null>(null);
  const { register, handleSubmit } = useForm<{
    count: number;
    difficulty: string;
    language: string;
  }>({
    defaultValues: { count: 10, difficulty: "medium", language: "english" },
  });

  const listQuery = useArtifactsQuery(documentId ?? 0, artifactPath, documentId !== null);
  const generateMutation = useGenerateArtifactMutation(documentId ?? 1, artifactPath);

  async function onGenerate(values: { count: number; difficulty: string; language: string }) {
    if (!documentId) return;
    await generateMutation.mutateAsync(values);
    await listQuery.refetch();
  }

  return (
    <section className="glass-panel p-6">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="display text-3xl">{title}</h2>

        <select
          className="input w-auto"
          value={documentId ?? ""}
          onChange={(e) => setDocumentId(Number(e.target.value))}
        >
          <option value="">Select Document</option>
          {documentsQuery.data?.map((doc) => (
            <option key={doc.id} value={doc.id}>
              {doc.original_name}
            </option>
          ))}
        </select>
      </div>

      <form className="mt-4 grid gap-2 md:grid-cols-4" onSubmit={handleSubmit(onGenerate)}>
        <input className="input" type="number" {...register("count", { valueAsNumber: true })} />
        <input className="input" placeholder="difficulty" {...register("difficulty")} />
        <input className="input" placeholder="language" {...register("language")} />
        <button className="btn-primary" type="submit" disabled={generateMutation.isPending || !documentId}>
          Generate
        </button>
      </form>

      <ul className="mt-4 grid gap-2 text-sm">
        {listQuery.data?.map((item) => (
          <li key={item.id} className="glass-panel p-3">
            <ArtifactRenderer artifact={{ id: item.id, artifact_type: artifactPath, payload: item.payload, created_at: item.created_at }} />
          </li>
        ))}
      </ul>
    </section>
  );
}

function DocumentsPage() {
  const { isAuthenticated } = useAuth();
  const query = useDocumentsQuery(isAuthenticated);

  return (
    <section className="glass-panel p-6">
      <h2 className="display text-3xl">Your Documents</h2>

      {query.isLoading ? (
        <div className="mt-4 grid gap-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 w-full animate-pulse rounded-lg bg-[var(--glass)]" />
          ))}
        </div>
      ) : query.error ? (
        <p className="text-red-500">{normalizeApiError(query.error)}</p>
      ) : (
        <ul className="mt-4 grid gap-2 text-sm">
          {query.data?.map((doc) => (
            <li key={doc.id} className="glass-panel p-3 flex justify-between items-center">
              <div>
                <span className="font-semibold">{doc.original_name}</span>
                <span className="text-xs text-[var(--muted)] ml-2">{doc.processing_status}</span>
              </div>
              <Link className="btn-ghost text-xs" to={`/documents/${doc.id}`}>
                View
              </Link>
            </li>
          ))}
          {!query.data?.length && (
            <p className="text-center py-8 text-[var(--muted)]">No documents uploaded yet.</p>
          )}
        </ul>
      )}
    </section>
  );
}

function ContentPage({ title, hint }: { title: string; hint: string }) {
  return (
    <section className="glass-panel p-6">
      <h2 className="display text-3xl">{title}</h2>
      <p className="mt-3 text-[var(--muted)]">{hint}</p>
    </section>
  );
}

function NotFoundPage() {
  return (
    <main className="hero-grid flex min-h-screen items-center justify-center p-6 text-[var(--text)]">
      <section className="glass-panel w-full max-w-xl p-8 text-center">
        <p className="caps">404</p>
        <h1 className="display mt-2 text-5xl">Page Not Found</h1>
        <Link className="btn-primary mt-6 inline-flex" to="/">
          Go Home
        </Link>
      </section>
    </main>
  );
}

export default function App() {
  const [isDark, setIsDark] = useState(false);

  return (
    <DocumentProvider documents={[]}>
      <Routes>
        <Route path="/" element={<PublicLayout title="AI Learning Assistant For Serious Students" subtitle="A modern SaaS workflow for document intelligence, adaptive assessments, and personalized planning." />} />
        <Route path="/features" element={<PublicLayout title="Features" subtitle="Chat, flashcards, MCQs, notes, quizzes, translation, roadmap, and planner." />} />
        <Route path="/pricing" element={<PublicLayout title="Pricing" subtitle="Simple academic pricing tiers with unlimited learning momentum." />} />
        <Route path="/about" element={<PublicLayout title="About" subtitle="Built for portfolio-grade full stack and AI engineering excellence." />} />
        <Route path="/contact" element={<PublicLayout title="Contact" subtitle="Reach out for collaboration, demos, and support." />} />

        <Route path="/login" element={<AuthPage title="Login" mode="login" />} />
        <Route path="/register" element={<AuthPage title="Register" mode="register" />} />
        <Route path="/forgot-password" element={<ContentPage title="Forgot Password" hint="Reset flow will be connected after backend reset-token APIs are added." />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout isDark={isDark} setIsDark={setIsDark} />}>
            <Route path="/dashboard" element={<DashboardHome />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/flashcards" element={<ArtifactPage title="Flashcards" artifactPath="flashcards" />} />
            <Route path="/mcqs" element={<ArtifactPage title="MCQs" artifactPath="mcqs" />} />
            <Route path="/quiz" element={<ArtifactPage title="Quiz" artifactPath="quiz" />} />
            <Route path="/study-notes" element={<ArtifactPage title="Study Notes" artifactPath="notes" />} />
            <Route path="/profile" element={<ContentPage title="Profile" hint="Update personal info and avatar." />} />
            <Route path="/settings" element={<ContentPage title="Settings" hint="Theme, password, delete account, and API preferences." />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </DocumentProvider>
  );
}
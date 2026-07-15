import { type ReactNode, useMemo, useState } from "react";
import { motion } from "framer-motion";
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

import { useAuth } from "./AuthContext";
import { useDocumentsQuery } from "./hooks";

type NavItem = { label: string; path: string; icon: ReactNode };

const dashboardNav: NavItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: <LayoutDashboard size={18} /> },
  { label: "Upload", path: "/upload", icon: <Upload size={18} /> },
  { label: "Document Details", path: "/documents", icon: <FileText size={18} /> },
  { label: "AI Chat", path: "/chat", icon: <Brain size={18} /> },
  { label: "Flashcards", path: "/flashcards", icon: <BookOpen size={18} /> },
  { label: "MCQs", path: "/mcqs", icon: <FileText size={18} /> },
  { label: "Quiz", path: "/quiz", icon: <Brain size={18} /> },
  { label: "Study Notes", path: "/study-notes", icon: <BookOpen size={18} /> },
  { label: "Profile", path: "/profile", icon: <User size={18} /> },
  { label: "Settings", path: "/settings", icon: <Settings size={18} /> },
];

type DashboardLayoutProps = {
  isDark: boolean;
  setIsDark: (v: boolean) => void;
  children: ReactNode;
};

export function DashboardLayout({ isDark, setIsDark, children }: DashboardLayoutProps) {
  const location = useLocation();
  const { logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const title = useMemo(() => {
    const found = dashboardNav.find((item) => location.pathname.startsWith(item.path));
    return found?.label ?? "Dashboard";
  }, [location.pathname]);

  return (
    <div className={isDark ? "theme-dark" : "theme-light"}>
      <div className="dashboard-wrap min-h-screen text-[var(--text)]">
        {/* Mobile menu button */}
        <button
          className="icon-btn fixed left-4 top-4 z-50 md:hidden"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle menu"
        >
          {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
        </button>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <aside
          className={`glass-panel fixed z-40 m-3 flex h-[calc(100vh-1.5rem)] w-64 flex-col gap-2 p-4 transition-transform md:static md:translate-x-0 ${
            sidebarOpen ? "translate-x-0" : "-translate-x-[110%]"
          }`}
        >
          <p className="caps mb-2">Acadexa AI</p>
          {dashboardNav.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="side-link"
              onClick={() => setSidebarOpen(false)}
            >
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

          {children}
        </div>
      </div>
    </div>
  );
}
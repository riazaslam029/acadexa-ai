import { useState } from "react";
import { Copy, Download, FileText, HelpCircle, List, BookOpen, Brain, Map, Calendar } from "lucide-react";

type ArtifactResponse = {
  id: number;
  artifact_type: string;
  payload: Record<string, unknown>;
  created_at: string;
};

type ArtifactRendererProps = {
  artifact: ArtifactResponse;
};

export function ArtifactRenderer({ artifact }: ArtifactRendererProps) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(artifact.payload, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const downloadJson = () => {
    const dataStr = JSON.stringify(artifact.payload, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${artifact.artifact_type}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderContent = () => {
    const payload = artifact.payload;

    switch (artifact.artifact_type) {
      case "flashcards": {
        const flashcards = payload.flashcards || [];
        return (
          <div className="grid gap-4">
            {flashcards.map((card: any, index: number) => (
              <div key={index} className="glass-panel p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs text-[var(--muted)]">Card {index + 1}</span>
                </div>
                <h4 className="font-semibold mb-2">Question:</h4>
                <p className="mb-3">{card.question}</p>
                <h4 className="font-semibold mb-2">Answer:</h4>
                <p>{card.answer}</p>
              </div>
            ))}
          </div>
        );
      }

      case "mcqs": {
        const mcqs = payload.mcqs || [];
        return (
          <div className="grid gap-4">
            {mcqs.map((q: any, index: number) => (
              <div key={index} className="glass-panel p-4">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs text-[var(--muted)]">Question {index + 1}</span>
                  <span className="text-xs px-2 py-1 rounded bg-[var(--brand)]/20 text-[var(--brand)]">
                    {q.difficulty}
                  </span>
                </div>
                <h4 className="font-semibold mb-2">{q.question}</h4>
                <div className="space-y-1 mb-3">
                  {q.options?.map((opt: string, optIdx: number) => (
                    <div key={optIdx} className="flex items-center">
                      <span className="font-bold mr-2">{String.fromCharCode(65 + optIdx)}.</span>
                      <span>{opt}</span>
                    </div>
                  ))}
                </div>
                <div className="glass-panel p-2 text-sm">
                  <strong>Correct Answer:</strong> {q.correct_answer}
                </div>
                {q.explanation && (
                  <div className="mt-2 text-sm text-[var(--muted)]">
                    <strong>Explanation:</strong> {q.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>
        );
      }

      case "key_points": {
        const points = payload.key_points || [];
        return (
          <div className="glass-panel p-4">
            <ul className="space-y-2">
              {points.map((point: string, index: number) => (
                <li key={index} className="flex items-start">
                  <span className="text-[var(--brand)] font-bold mr-2">•</span>
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        );
      }

      case "study_notes": {
        const notes = payload.study_notes || "";
        return (
          <div className="glass-panel p-4 max-h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap font-mono text-sm">{notes}</pre>
          </div>
        );
      }

      case "quizzes": {
        const quiz = payload.quiz || [];
        return (
          <div className="grid gap-4">
            {quiz.map((q: any, index: number) => (
              <div key={index} className="glass-panel p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs text-[var(--muted)]">Question {index + 1}</span>
                  <span className="text-xs px-2 py-1 rounded bg-[var(--brand)]/20 text-[var(--brand)]">
                    {q.difficulty}
                  </span>
                </div>
                <h4 className="font-semibold mb-2">{q.question}</h4>
                <p className="mb-2"><strong>Answer:</strong> {q.answer}</p>
              </div>
            ))}
          </div>
        );
      }

      case "translations": {
        const translation = payload.translation || "";
        const language = payload.language || "Unknown";
        return (
          <div className="glass-panel p-4">
            <div className="flex items-center mb-3">
              <Globe className="mr-2" size={20} />
              <h3 className="text-lg font-semibold">Translation to {language}</h3>
            </div>
            <div className="whitespace-pre-wrap">{translation}</div>
          </div>
        );
      }

      case "eli5": {
        const eli5 = payload.eli5 || "";
        return (
          <div className="glass-panel p-4">
            <div className="flex items-center mb-3">
              <HelpCircle className="mr-2" size={20} />
              <h3 className="text-lg font-semibold">Explain Like I'm 5</h3>
            </div>
            <div className="whitespace-pre-wrap">{eli5}</div>
          </div>
        );
      }

      case "roadmap": {
        const roadmap = payload.roadmap || [];
        return (
          <div className="glass-panel p-4">
            <div className="flex items-center mb-4">
              <Map className="mr-2" size={20} />
              <h3 className="text-lg font-semibold">Learning Roadmap</h3>
            </div>
            <div className="space-y-3">
              {roadmap.map((step: any, index: number) => (
                <div key={index} className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--brand)] flex items-center justify-center text-white font-bold">
                    {step.step || index + 1}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold">{step.title}</h4>
                    <p className="text-sm text-[var(--muted)]">{step.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      }

      case "study_plan": {
        const plan = payload.study_plan || {};
        const dailyPlan = plan.daily_plan || [];
        return (
          <div className="glass-panel p-4">
            <div className="flex items-center mb-4">
              <Calendar className="mr-2" size={20} />
              <h3 className="text-lg font-semibold">Study Plan</h3>
            </div>
            <div className="mb-3">
              <strong>Estimated Days:</strong> {plan.estimated_days || "Unknown"}
            </div>
            <div>
              <h4 className="font-semibold mb-2">Daily Plan:</h4>
              <ol className="space-y-2">
                {dailyPlan.map((day: string, index: number) => (
                  <li key={index} className="flex items-start">
                    <span className="text-xs text-[var(--muted)] mr-2">{index + 1}.</span>
                    <span>{day}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        );
      }

      default:
        return (
          <div className="glass-panel p-4">
            <pre className="overflow-auto text-xs">{JSON.stringify(payload, null, 2)}</pre>
          </div>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={copyToClipboard}
          className="btn-ghost text-xs flex items-center gap-1"
          aria-label="Copy to clipboard"
        >
          <Copy size={16} />
          {copied ? "Copied!" : "Copy JSON"}
        </button>
        <button
          onClick={downloadJson}
          className="btn-ghost text-xs flex items-center gap-1"
          aria-label="Download as JSON"
        >
          <Download size={16} />
          Download
        </button>
      </div>

      {/* Content */}
      {renderContent()}
    </div>
  );
}

function Globe(props: any) {
  return <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M4.93 4.93l14.14 14.14"></path></svg>;
}
import { createContext, type ReactNode, useCallback, useContext, useMemo, useState } from "react";
import type { DocumentResponse } from "./api";

type DocumentContextType = {
  selectedDocumentId: number | null;
  selectedDocument: DocumentResponse | null;
  selectDocument: (doc: DocumentResponse) => void;
  clearSelection: () => void;
};

const DocumentContext = createContext<DocumentContextType | null>(null);

export function DocumentProvider({ children }: { children: ReactNode }) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null);
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);

  const selectedDocument = useMemo(() => {
    if (!selectedDocumentId) return null;
    return documents.find((d) => d.id === selectedDocumentId) || null;
  }, [selectedDocumentId, documents]);

  const selectDocument = useCallback((doc: DocumentResponse) => {
    setSelectedDocumentId(doc.id);
    setDocuments((prev) => {
      if (prev.find((d) => d.id === doc.id)) return prev;
      return [...prev, doc];
    });
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedDocumentId(null);
  }, []);

  return (
    <DocumentContext.Provider
      value={{
        selectedDocumentId,
        selectedDocument,
        selectDocument,
        clearSelection,
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
}

export function useDocumentContext() {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error("useDocumentContext must be used within DocumentProvider");
  }
  return context;
}
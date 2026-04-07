import { useState, useCallback, useEffect, useRef } from "react";
import { getContentByHash, saveContent } from "./db";

interface MCQ {
  question: string;
  options: string[];
  answer?: string;
}

interface Flashcard {
  term: string;
  definition: string;
}

interface StudyResult {
  mcqs: MCQ[];
  theory: string[];
  flashcards: Flashcard[];
  summary: string;
}

interface UseStudyReturn {
  processDocument: (file: File) => Promise<StudyResult>;
  loading: boolean;
  error: string | null;
  result: StudyResult | null;
  isFromCache: boolean;
}

// Request timeout: 5 minutes
const REQUEST_TIMEOUT_MS = 5 * 60 * 1000;

export function useStudy(): UseStudyReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<StudyResult | null>(null);
  const [isFromCache, setIsFromCache] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const generateContentHash = useCallback((file: File): string => {
    const str = `${file.name}-${file.size}-${file.lastModified}`;
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    return `hash-${Math.abs(hash).toString(16)}`;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cancel any pending requests when component unmounts
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const processDocument = useCallback(
    async (file: File): Promise<StudyResult> => {
      // Cancel any previous requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      abortControllerRef.current = new AbortController();
      setLoading(true);
      setError(null);

      try {
        const contentHash = generateContentHash(file);
        console.log(`[useStudy] Generated content hash: ${contentHash}`);

        console.log("[useStudy] Checking local database...");
        const cachedData = await getContentByHash(contentHash);

        if (cachedData && cachedData.content) {
          console.log("[useStudy] Found in local database, using cached data");

          try {
            const parsedMcq = JSON.parse(cachedData.content.mcq || "[]");
            const parsedFlashcards = JSON.parse(
              cachedData.content.flashcards || "[]"
            );

            const studyResult: StudyResult = {
              mcqs: Array.isArray(parsedMcq) ? parsedMcq : [],
              theory: [],
              flashcards: Array.isArray(parsedFlashcards) ? parsedFlashcards : [],
              summary: cachedData.content.summary || "",
            };

            setResult(studyResult);
            setIsFromCache(true);
            setLoading(false);
            return studyResult;
          } catch (parseError) {
            console.error("[useStudy] Failed to parse cached data:", parseError);
            throw new Error("Failed to parse cached data");
          }
        }

        console.log("[useStudy] Not found in cache, calling backend API...");

        const formData = new FormData();
        formData.append("file", file);

        // Create timeout promise
        const timeoutPromise = new Promise<Response>((_, reject) => {
          setTimeout(() => reject(new Error("Request timeout after 5 minutes")), REQUEST_TIMEOUT_MS);
        });

        const fetchPromise = fetch("http://127.0.0.1:8000/generate", {
          method: "POST",
          body: formData,
          signal: abortControllerRef.current.signal,
        });

        const response = await Promise.race([fetchPromise, timeoutPromise]);

        if (!response.ok) {
          const message = `Backend request failed: ${response.status} ${response.statusText}`;
          console.error(`[useStudy] ${message}`);
          throw new Error(message);
        }

        const data = await response.json();
        console.log("[useStudy] Backend response received:", data);

        const studyResult: StudyResult = {
          mcqs: Array.isArray(data.mcqs) ? data.mcqs : [],
          theory: Array.isArray(data.theory) ? data.theory : [],
          flashcards: Array.isArray(data.flashcards) ? data.flashcards : [],
          summary: typeof data.summary === "string" ? data.summary : "",
        };

        try {
          await saveContent(file.name, contentHash, {
            mcq: studyResult.mcqs,
            flashcards: studyResult.flashcards,
            summary: studyResult.summary,
          });
          console.log("[useStudy] Data saved to local database");
        } catch (saveError) {
          console.warn(
            "[useStudy] Failed to save to database, continuing anyway:",
            saveError
          );
        }

        setResult(studyResult);
        setIsFromCache(false);
        setLoading(false);
        return studyResult;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "An unknown error occurred";
        console.error("[useStudy] Error:", errorMessage);
        setError(errorMessage);
        setLoading(false);
        throw err;
      }
    },
    [generateContentHash]
  );

  return {
    processDocument,
    loading,
    error,
    result,
    isFromCache,
  };
}

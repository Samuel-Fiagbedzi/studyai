import { invoke } from "@tauri-apps/api/core";

const DB_URL = "sqlite:studyai.db";

interface Document {
  id: number;
  name: string;
  content_hash: string;
}

interface GeneratedContent {
  id: number;
  document_id: number;
  mcq: string;
  flashcards: string;
  summary: string;
}

interface ContentData {
  mcq: unknown[];
  flashcards: unknown[];
  summary: string;
}

interface DocumentWithContent extends Document {
  content: GeneratedContent | null;
}

export async function initDB(): Promise<void> {
  try {
    await invoke("plugin:sql|load", {
      url: DB_URL,
    });

    await invoke("plugin:sql|execute", {
      db: DB_URL,
      query: `
        CREATE TABLE IF NOT EXISTS documents (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          content_hash TEXT NOT NULL UNIQUE,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
      `,
    });

    await invoke("plugin:sql|execute", {
      db: DB_URL,
      query: `
        CREATE TABLE IF NOT EXISTS generated_content (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          document_id INTEGER NOT NULL,
          mcq TEXT,
          flashcards TEXT,
          summary TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        );
      `,
    });

    // Create indexes for frequently queried columns
    await invoke("plugin:sql|execute", {
      db: DB_URL,
      query: "CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash);",
    });

    await invoke("plugin:sql|execute", {
      db: DB_URL,
      query: "CREATE INDEX IF NOT EXISTS idx_generated_content_document_id ON generated_content(document_id);",
    });

    console.log("Database initialized successfully");
  } catch (error) {
    console.error("Failed to initialize database:", error);
    throw new Error(`Database initialization failed: ${error}`);
  }
}

export async function saveContent(
  documentName: string,
  contentHash: string,
  data: ContentData
): Promise<number> {
  try {
    const insertDocResult = await invoke<{ lastInsertId: number }>(
      "plugin:sql|execute",
      {
        db: DB_URL,
        query: `
          INSERT INTO documents (name, content_hash)
          VALUES (?, ?)
        `,
        values: [documentName, contentHash],
      }
    );

    const documentId = insertDocResult.lastInsertId;

    await invoke("plugin:sql|execute", {
      db: DB_URL,
      query: `
        INSERT INTO generated_content (document_id, mcq, flashcards, summary)
        VALUES (?, ?, ?, ?)
      `,
      values: [
        documentId,
        JSON.stringify(data.mcq),
        JSON.stringify(data.flashcards),
        data.summary,
      ],
    });

    console.log(`Content saved with document ID: ${documentId}`);
    return documentId;
  } catch (error) {
    console.error("Failed to save content:", error);
    throw new Error(`Failed to save content: ${error}`);
  }
}

export async function getContentByHash(
  contentHash: string
): Promise<DocumentWithContent | null> {
  try {
    const result = await invoke<
      Array<{
        doc_id: number;
        doc_name: string;
        doc_hash: string;
        content_id: number | null;
        mcq: string | null;
        flashcards: string | null;
        summary: string | null;
      }>
    >("plugin:sql|select", {
      db: DB_URL,
      query: `
        SELECT
          d.id as doc_id,
          d.name as doc_name,
          d.content_hash as doc_hash,
          gc.id as content_id,
          gc.mcq,
          gc.flashcards,
          gc.summary
        FROM documents d
        LEFT JOIN generated_content gc ON d.id = gc.document_id
        WHERE d.content_hash = ?
      `,
      values: [contentHash],
    });

    if (!result || result.length === 0) {
      return null;
    }

    const row = result[0];
    const document: DocumentWithContent = {
      id: row.doc_id,
      name: row.doc_name,
      content_hash: row.doc_hash,
      content: null,
    };

    if (row.content_id !== null) {
      document.content = {
        id: row.content_id,
        document_id: row.doc_id,
        mcq: row.mcq || "[]",
        flashcards: row.flashcards || "[]",
        summary: row.summary || "",
      };
    }

    return document;
  } catch (error) {
    console.error("Failed to get content by hash:", error);
    throw new Error(`Failed to get content by hash: ${error}`);
  }
}

export async function getAllDocuments(limit: number = 1000): Promise<DocumentWithContent[]> {
  try {
    const result = await invoke<
      Array<{
        doc_id: number;
        doc_name: string;
        doc_hash: string;
        content_id: number | null;
        mcq: string | null;
        flashcards: string | null;
        summary: string | null;
      }>
    >("plugin:sql|select", {
      db: DB_URL,
      query: `
        SELECT
          d.id as doc_id,
          d.name as doc_name,
          d.content_hash as doc_hash,
          gc.id as content_id,
          gc.mcq,
          gc.flashcards,
          gc.summary
        FROM documents d
        LEFT JOIN generated_content gc ON d.id = gc.document_id
        ORDER BY d.created_at DESC
        LIMIT ?
      `,
      values: [limit],
    });

    if (!result) {
      return [];
    }

    const documentsMap = new Map<number, DocumentWithContent>();

    for (const row of result) {
      if (!documentsMap.has(row.doc_id)) {
        documentsMap.set(row.doc_id, {
          id: row.doc_id,
          name: row.doc_name,
          content_hash: row.doc_hash,
          content: null,
        });
      }

      if (row.content_id !== null) {
        const doc = documentsMap.get(row.doc_id)!;
        doc.content = {
          id: row.content_id,
          document_id: row.doc_id,
          mcq: row.mcq || "[]",
          flashcards: row.flashcards || "[]",
          summary: row.summary || "",
        };
      }
    }

    return Array.from(documentsMap.values());
  } catch (error) {
    console.error("Failed to get all documents:", error);
    throw new Error(`Failed to get all documents: ${error}`);
  }
}

export function parseJSONField<T>(jsonString: string, fallback: T): T {
  try {
    return JSON.parse(jsonString) as T;
  } catch {
    console.warn(`Failed to parse JSON field, returning fallback:`, jsonString);
    return fallback;
  }
}

export async function deleteDocument(documentId: number): Promise<void> {
  try {
    await invoke("plugin:sql|execute", {
      db: DB_URL,
      query: `DELETE FROM documents WHERE id = ?`,
      values: [documentId],
    });

    console.log(`Document ${documentId} deleted successfully`);
  } catch (error) {
    console.error("Failed to delete document:", error);
    throw new Error(`Failed to delete document: ${error}`);
  }
}

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use tauri_plugin_sql::{Builder as SqlBuilder, Migration, MigrationKind, PluginConfig};

#[tauri::command]
fn greet(name: &str) -> String {
  format!("Hello, {}! You've been greeted from Rust!", name)
}

fn initialize_database<R: tauri::Runtime>() -> tauri::plugin::TauriPlugin<R, Option<PluginConfig>> {
  SqlBuilder::new().add_migrations(
    "sqlite:studyai.db",
    vec![Migration {
      version: 1,
      description: "Create documents and generated content tables",
      sql: r#"
        CREATE TABLE IF NOT EXISTS documents (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          content_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS generated_content (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          document_id INTEGER NOT NULL,
          mcq TEXT,
          flashcards TEXT,
          summary TEXT,
          FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        );
      "#,
      kind: MigrationKind::Up,
    }],
  ).build()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(initialize_database())
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

import { useState } from "react";
import AuditTable from "./components/AuditTable";
import Dashboard from "./components/Dashboard";
import RequestTester from "./components/RequestTester";
import "./App.css";

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Aegis</h1>
        <p>AI-agent guardrail layer — prompt-injection screening, action policy, audit trail.</p>
      </header>

      <main>
        <RequestTester onSubmitted={() => setRefreshKey((k) => k + 1)} />
        <Dashboard refreshKey={refreshKey} />
        <AuditTable refreshKey={refreshKey} />
      </main>
    </div>
  );
}

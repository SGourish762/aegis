import { useState } from "react";
import AuditTable from "./components/AuditTable";
import ContentFirewall from "./components/ContentFirewall";
import Dashboard from "./components/Dashboard";
import RequestTester from "./components/RequestTester";
import "./App.css";

function ShieldMark() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 2.5l7.5 3v6c0 5-3.2 8.7-7.5 10-4.3-1.3-7.5-5-7.5-10v-6l7.5-3z"
        fill="var(--accent)"
        fillOpacity="0.18"
        stroke="var(--accent)"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path
        d="M8.7 12.2l2.3 2.3 4.3-4.7"
        stroke="var(--accent)"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);
  const bump = () => setRefreshKey((k) => k + 1);

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-brand">
          <ShieldMark />
          <span>Aegis</span>
        </div>
        <div className="nav-links">
          <a href="#firewall">Content firewall</a>
          <a href="#try">Try it</a>
          <a href="#activity">Activity</a>
          <a
            href="https://github.com/SGourish762/aegis"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>
        </div>
      </nav>

      <header className="hero">
        <div className="hero-glow" aria-hidden="true" />
        <span className="eyebrow">AI-agent guardrail layer</span>
        <h1>
          Stop prompt injection
          <br />
          before it reaches your AI.
        </h1>
        <p className="hero-sub">
          Deterministic, rule-based screening for what your agent reads, and a
          deny-by-default policy engine for what it's allowed to do — fast,
          free, auditable, and it never depends on an LLM to protect you from
          one.
        </p>
        <div className="hero-cta">
          <a href="#firewall" className="btn btn-primary">
            See it stop an attack
          </a>
          <a href="#try" className="btn btn-ghost">
            Try your own input
          </a>
        </div>
      </header>

      <main>
        <ContentFirewall />
        <RequestTester onSubmitted={bump} />
        <div id="activity">
          <Dashboard refreshKey={refreshKey} />
          <AuditTable refreshKey={refreshKey} />
        </div>
      </main>

      <footer className="footer">
        <span>Aegis — deterministic prompt-injection detection + agent policy engine.</span>
        <a href="https://github.com/SGourish762/aegis" target="_blank" rel="noreferrer">
          Source on GitHub
        </a>
      </footer>
    </div>
  );
}

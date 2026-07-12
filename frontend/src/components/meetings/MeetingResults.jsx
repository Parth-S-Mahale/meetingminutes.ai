import { useState } from "react";
import StatusBadge from "../../common/StatusBadge";
import { useMeetings } from "../../context/MeetingContext";

const formatDate = (date) => new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short",
}).format(new Date(date));

function Transcript({ transcript }) {
  const wordCount = transcript?.trim().split(/\s+/).filter(Boolean).length || 0;
  return <article className="transcript-panel">
    <div className="transcript-toolbar"><div><p className="eyebrow">Source transcript</p><h3>Full transcription</h3></div><span>{wordCount} words</span></div>
    <p>{transcript || "No transcript is available for this meeting."}</p>
  </article>;
}

function KeyDecisions({ decisions }) {
  return <article className="decision-panel">
    <div className="panel-heading"><div><p className="eyebrow">AI extracted</p><h3>Key decisions</h3></div><span>{decisions.length}</span></div>
    {decisions.length ? <ol className="decision-list">{decisions.map((decision, index) => <li key={`${decision}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{decision}</p></li>)}</ol> : <p className="muted">No decisions were identified in this meeting.</p>}
  </article>;
}

function ActionItems({ actionItems }) {
  return <article className="action-panel">
    <div className="panel-heading"><div><p className="eyebrow">Follow-up work</p><h3>Action items</h3></div><span>{actionItems.length}</span></div>
    {actionItems.length ? <div className="action-list">{actionItems.map((item, index) => <article className="action-card" key={`${item.task}-${index}`}><span className="action-number">{String(index + 1).padStart(2, "0")}</span><div><h4>{item.task || "Unspecified task"}</h4><dl><div><dt>Owner</dt><dd>{item.owner || "Unassigned"}</dd></div><div><dt>Deadline</dt><dd>{item.deadline || "Not specified"}</dd></div></dl></div></article>)}</div> : <p className="muted">No action items were identified in this meeting.</p>}
  </article>;
}

export default function MeetingResults({ meeting }) {
  const [tab, setTab] = useState("summary");
  const { isProcessing, regenerateAnalysis } = useMeetings();
  const decisions = Array.isArray(meeting.key_decisions) ? meeting.key_decisions : [];
  const actionItems = Array.isArray(meeting.action_items) ? meeting.action_items : [];
  const tabs = [
    ["summary", "Summary"],
    ["decisions", `Key decisions (${decisions.length})`],
    ["actions", `Action items (${actionItems.length})`],
    ["transcript", "Transcript"],
  ];
  const rerunAnalysis = async () => {
    try {
      await regenerateAnalysis(meeting.id);
    } catch {
      // The context displays the request error in the shared alert.
    }
  };

  return <section className="results">
    <div className="results-header"><div><p className="eyebrow">Meeting minutes</p><h2>{meeting.title || meeting.original_filename}</h2><p className="metadata">Processed {formatDate(meeting.created_at)}{meeting.language ? ` · ${meeting.language}` : ""}</p></div><div className="result-actions"><StatusBadge status={meeting.status} /><button className="secondary-button" type="button" disabled={isProcessing || !meeting.transcript} onClick={rerunAnalysis}>{isProcessing ? "Regenerating…" : "Regenerate analysis"}</button></div></div>
    {meeting.error_message ? <div className="alert">{meeting.error_message}</div> : <>
      <div className="result-tabs" role="tablist" aria-label="Meeting results">{tabs.map(([id, label]) => <button key={id} role="tab" aria-selected={tab === id} className={tab === id ? "active" : ""} onClick={() => setTab(id)}>{label}</button>)}</div>
      {tab === "summary" && <article className="summary-card"><p className="eyebrow">Executive summary</p><p>{meeting.summary || "No summary was generated."}</p></article>}
      {tab === "decisions" && <KeyDecisions decisions={decisions} />}
      {tab === "actions" && <ActionItems actionItems={actionItems} />}
      {tab === "transcript" && <Transcript transcript={meeting.transcript} />}
    </>}
  </section>;
}

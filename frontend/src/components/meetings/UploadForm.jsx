import { useRef, useState } from "react";
import { useMeetings } from "../../context/MeetingContext";

const allowedTypes = [".mp3", ".wav", ".m4a", ".aac", ".mp4"];

export default function UploadForm() {
  const inputRef = useRef(null);
  const { isProcessing, uploadProgress, processMeeting } = useMeetings();
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState("");
  const chooseFile = (candidate) => {
    if (!candidate) return;
    const extension = `.${candidate.name.split(".").pop()?.toLowerCase()}`;
    if (!allowedTypes.includes(extension)) return setValidationError(`Unsupported file type. Upload one of: ${allowedTypes.join(", ")}.`);
    setFile(candidate); setValidationError("");
  };
  const submit = async (event) => {
    event.preventDefault();
    if (!file) return setValidationError("Choose an audio recording before processing.");
    try { await processMeeting(file, title); setFile(null); setTitle(""); inputRef.current.value = ""; } catch { /* shared error alert */ }
  };
  return <form className="upload-card" onSubmit={submit}><div className="section-heading"><span className="step">01</span><div><h2>New meeting</h2><p>Start with an audio recording.</p></div></div><label className="field-label" htmlFor="title">Meeting title <span>optional</span></label><input id="title" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Product planning" maxLength="255" /><input ref={inputRef} className="sr-only" id="audio" type="file" accept={allowedTypes.join(",")} onChange={(event) => chooseFile(event.target.files?.[0])} /><label htmlFor="audio" className={`dropzone ${isDragging ? "dragging" : ""}`} onDragOver={(event) => { event.preventDefault(); setIsDragging(true); }} onDragLeave={() => setIsDragging(false)} onDrop={(event) => { event.preventDefault(); setIsDragging(false); chooseFile(event.dataTransfer.files?.[0]); }}><span className="upload-icon">↑</span>{file ? <><strong>{file.name}</strong><small>{(file.size / 1024 / 1024).toFixed(1)} MB · Ready to process</small></> : <><strong>Drop your recording here</strong><small>or click to browse · MP3, WAV, M4A, AAC, MP4</small></>}</label>{validationError && <p className="inline-error">{validationError}</p>}{isProcessing && <div className="progress"><span style={{ width: `${uploadProgress || 8}%` }} /><small>{uploadProgress < 100 ? `Uploading ${uploadProgress}%` : "Transcribing and generating your minutes…"}</small></div>}<button className="primary-button" disabled={isProcessing}>{isProcessing ? "Processing meeting…" : "Create meeting minutes →"}</button></form>;
}

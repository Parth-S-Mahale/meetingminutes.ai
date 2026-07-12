import api from "./client";

export async function uploadMeeting(file, title, onUploadProgress) {
  const data = new FormData();
  data.append("file", file);
  if (title.trim()) data.append("title", title.trim());

  const response = await api.post("/meetings/upload", data, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return response.data;
}

export async function getMeetings() {
  const response = await api.get("/meetings");
  return response.data.meetings;
}

export async function getMeeting(id) {
  const response = await api.get(`/meetings/${id}`);
  return response.data;
}

export async function regenerateMeetingAnalysis(id) {
  const response = await api.post(`/meetings/${id}/summarize`);
  return response.data;
}

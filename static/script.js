async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

document.getElementById("correctBtn").addEventListener("click", async () => {
  const text = document.getElementById("inputText").value;
  if (!text.trim()) return;
  const { corrected } = await postJSON("/api/correct", { text });
  document.getElementById("outputText").innerText = corrected;
});

document.getElementById("uploadBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) return;
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  const res = await fetch("/api/upload", { method: "POST", body: formData });
  if (res.ok) {
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileInput.files[0].name.replace(/\.txt$/, "_corrected.txt");
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url);
  }
});
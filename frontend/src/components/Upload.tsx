export default function UploadSection() {
    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
  
      const formData = new FormData();
      formData.append("file", file);
  
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
  
      const data = await res.json();
      alert(`✅ File uploaded: ${data.chunks_ready} chunks indexed`);
    };
  
    return (
      <div className="mt-4">
        <label className="block mb-2 font-semibold">Upload Patent JSON:</label>
        <input type="file" accept=".json" onChange={handleUpload} />
      </div>
    );
  }
  
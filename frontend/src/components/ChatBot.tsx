// import { useState } from "react";

// export default function Chatbot() {
//   const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
//   const [input, setInput] = useState("");

//   const handleSend = async () => {
//     if (!input.trim()) return;
  
//     const newMessage = { sender: "user", text: input };
//     setMessages((prev) => [...prev, newMessage]);
//     setInput("");
  
//     try {
//         const res = await fetch("http://127.0.0.1:8001/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message: input }),
//       });
  
//       const data = await res.json();
//       const botMessage = { sender: "bot", text: data.reply };
//       setMessages((prev) => [...prev, botMessage]);
//     } catch (err) {
//       setMessages((prev) => [
//         ...prev,
//         { sender: "bot", text: "❌ Error connecting to server." },
//       ]);
//     }
//   };  

//   return (
//     <main className="flex-1 p-6 flex flex-col justify-between">
//       <div className="overflow-y-auto space-y-4 mb-4">
//         {messages.map((msg, i) => (
//           <div
//             key={i}
//             className={`max-w-xl px-4 py-2 rounded-lg ${
//               msg.sender === "user"
//                 ? "ml-auto bg-green-100 text-right"
//                 : "mr-auto bg-white border"
//             }`}
//           >
//             {msg.text}
//           </div>
//         ))}
//       </div>

//       <div className="flex gap-2">
//         <input
//           className="flex-1 px-4 py-2 border rounded-lg"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           placeholder="Ask something about a patent..."
//         />
//         <button
//           onClick={handleSend}
//           className="px-4 py-2 bg-green-600 text-white rounded-lg"
//         >
//           ➤
//         </button>
//       </div>
//     </main>
//   );
// }

import { useState, useEffect, useRef } from "react";
import { ChevronDown, Send, Loader2, Upload } from "lucide-react";
// import { ChatMessage, sendChatMessage, getSuggestedQuestions, checkServerStatus, upload

export default function Chatbot() {
  // const [messages, setMessages] = useState<ChatMessage[]>([]);
  // const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState<string>("connecting");
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Working
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState("");

  // useEffect(() => {
  //   const checkStatus = async () => {
  //     try {
  //       const status = await checkServerStatus();
  //       setServerStatus(status.status);
        
  //       // if (status.status === "online") {
  //       //   loadSuggestedQuestions();
  //       // }
  //     } catch (error) {
  //       setServerStatus("offline");
  //     }
  //   };
    
  //   checkStatus();
  //   const interval = setInterval(checkStatus, 30000);
  //   return () => clearInterval(interval);
  // }, []);

  // const loadSuggestedQuestions = async () => {
  //   try {
  //     const questions = await getSuggestedQuestions();
  //     setSuggestedQuestions(questions);
  //   } catch (error) {
  //     console.error("Failed to load suggested questions:", error);
  //   }
  // };

  // useEffect(() => {
  //   messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  // }, [messages]);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    try {
      await uploadFile(file);

      async function uploadFile(file: File): Promise<void> {
        // Replace this with the actual implementation of the file upload logic
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://127.0.0.1:8001/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Failed to upload file");
        }
      }
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: `PDF "${file.name}" uploaded and processed successfully! You can now ask questions about it.`
      }]);
      // await loadSuggestedQuestions();
    } catch (error) {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: '❌ Failed to upload and process the PDF. Please try again.'
      }]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
  
    const newMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
  
    try {
        const res = await fetch("http://127.0.0.1:8001/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
  
      const data = await res.json();
      const botMessage = { sender: "bot", text: data.reply };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Error connecting to server." },
      ]);
    }
  };  

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
    setShowSuggestions(false);
  };

  return (
    <div className="flex flex-col h-full max-h-screen bg-gray-50">
      <header className="p-4 border-b bg-white flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <h1 className="text-xl font-semibold">Chat with PDF</h1>
          <div className="flex items-center">
            <span 
              className={`w-2 h-2 rounded-full mr-2 ${
                serverStatus === "online" 
                  ? "bg-green-500" 
                  : serverStatus === "ready" 
                  ? "bg-yellow-500" 
                  : "bg-red-500"
              }`}
            />
            <span className="text-sm text-gray-500">
              {serverStatus === "online" 
                ? "Connected" 
                : serverStatus === "ready" 
                ? "Ready" 
                : "Disconnected"}
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 p-4 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <h2 className="text-lg font-medium text-gray-700 mb-2">
              Welcome! Let's analyze your PDF document.
            </h2>
            <p className="text-gray-500 mb-4">
              Start chatting or upload a PDF to begin the analysis.
            </p>
          </div>
        )}

        <div className="space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`max-w-[80%] px-4 py-3 rounded-lg animate-fadeIn ${
                msg.sender === "user"
                  ? "ml-auto bg-green-100 text-gray-800"
                  : "mr-auto bg-white border border-gray-200 shadow-sm"
              }`}
            >
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div className="mr-auto bg-white border border-gray-200 rounded-lg px-4 py-3 flex items-center shadow-sm max-w-[80%]">
              <Loader2 size={16} className="mr-2 animate-spin text-green-600" />
              <span className="text-gray-500">Thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="p-4 border-t bg-white">
        {suggestedQuestions.length > 0 && (
          <div className="mb-2">
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              <span>Suggested questions</span>
              <ChevronDown 
                size={16} 
                className={`ml-1 transition-transform ${showSuggestions ? 'rotate-180' : ''}`} 
              />
            </button>
            
            {showSuggestions && (
              <div className="mt-2 space-y-2">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        
        <div className="flex items-center space-x-2">
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".json" //.pdf
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileUpload(file);
            }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            disabled={isUploading}
          >
            {isUploading ? (
              <Loader2 size={20} className="animate-spin text-gray-600" />
            ) : (
              <Upload size={20} className="text-gray-600" />
            )}
          </button>
          <textarea
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none max-h-32"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            // onKeyDown={handleKeyDown}
            placeholder={
              serverStatus === "online" 
                ? "Ask something about the document..." 
                : serverStatus === "ready" 
                ? "Upload a PDF to start chatting" 
                : "Server disconnected"
            }
            // disabled={serverStatus !== "online"}
            rows={1}
          />
          <button
            onClick={handleSend}
            // disabled={!input.trim() || isLoading || serverStatus !== "online"}
            className={`p-2 rounded-lg transition-colors ${
              !input.trim() || isLoading
                ? "bg-gray-200 text-gray-500"
                : "bg-green-600 text-white hover:bg-green-700"
            }`}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
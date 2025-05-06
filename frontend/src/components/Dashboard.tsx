import { Leaf } from "lucide-react";
import { Link, Outlet } from "react-router-dom";

export default function MainDashboard() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/pdf-upload" className="flex items-center space-x-2 px-4 py-2 bg-gray-800 rounded">
            <span>📄</span>
            <span>PDF Upload</span>
          </Link>
          <Link to="/chat" className="flex items-center space-x-2 px-4 py-2 bg-gray-800 rounded">
            <span>💬</span>
            <span>ChatBot</span>
          </Link>
        </nav>
      </aside>

      {/* Right side: Header + Routed content */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-6 bg-white shadow">
          <div className="flex items-center">
            <Leaf className="h-10 w-10 text-emerald-600" />
            <h1 className="ml-3 text-3xl font-bold text-gray-900">EcoPatent Analyzer</h1>
          </div>
        </header>

        {/* Render current route */}
        <Outlet />
      </div>
    </div>
  );
}
